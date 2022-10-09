bl_info = {
    'name': 'LMDL format',
    'author': 'RenViscoso',
    'version': (1, 0, 1),
    'blender': (3, 3, 0),
    'location': 'File > Import/Export',
    'description': 'Import LMDL files',
    'category': 'Import-Export',
}

import os
import bpy
import bmesh
import struct
from bpy.props import (
    CollectionProperty,
    StringProperty,
    BoolProperty,
)
from bpy_extras.io_utils import ImportHelper

class ImportLMDL(bpy.types.Operator, ImportHelper):
    '''Load a LMDL file'''
    bl_idname = 'import_model.lmdl'
    bl_label = 'Import LMDL'
    bl_options = {'UNDO'}

    files: CollectionProperty(
        name = 'File Path',
        description = 'File path used for importing the LMDL file',
        type = bpy.types.OperatorFileListElement,
    )

    hide_props_region: BoolProperty(
        name = 'Hide Operator Properties',
        description = 'Collapse the region displaying the operator settings',
        default = True,
    )

    directory: StringProperty()

    filename_ext = '.lmdl'
    filter_glob: StringProperty(default='*.lmdl', options={'HIDDEN'})

    # Main function
    def execute(self, context):
        
        for name in self.files:
            ImportLMDL.lmdl_load(self, context, self.directory, name.name)

        context.window.cursor_set('DEFAULT')

        return {'FINISHED'}
    
    # Read file fuction
    def lmdl_load(operator, context, file_directory, file_name: str):
        filedata = None

        with open(os.path.join(file_directory, file_name), 'rb') as file:
            # Check signature
            filedata = file.read()
            if not filedata.startswith(b'PII|BMDLT'):
                raise ValueError('Signature file error!')

        # Data types for struct.unpack()
        datatypes = {
            'flt': ['<f', 4],
            'short': ['<H', 2],
            'string': ['64s', 64]
        }
        
        # Data dictionaries
        positions = {}
        texcoords = {}
        vertexes = {}
        vertex_tris = {}
        materials = {}
        material_tris = {}
        bones = {}
        bonelinks = {}
        
        # Parse data into dictionaries
        # Data, chunk header, dictionary for chunk, number of values in one type of data, type of values
        ImportLMDL.read_block(filedata, b'positions', positions, 3, datatypes['flt'])
        ImportLMDL.read_block(filedata, b'texcoords', texcoords, 2, datatypes['flt'])
        ImportLMDL.read_block(filedata, b'vertexes', vertexes, 6, datatypes['short'])
        ImportLMDL.read_block(filedata, b'vertex_tris', vertex_tris, 3, datatypes['short'])
        ImportLMDL.read_block(filedata, b'materials', materials, 1, datatypes['string'])
        ImportLMDL.read_block(filedata, b'material_tris', material_tris, 1, datatypes['short'])
        ImportLMDL.read_block(filedata, b'bonelinks', bonelinks, 1, datatypes['short'])
        ImportLMDL.read_block(filedata, b'bones', bones, 3, datatypes['string'])
        
        object_name = file_name.lower().rstrip(operator.filename_ext)
        
        # Create a new mesh and a new object
        mesh = bpy.data.meshes.new(f"{object_name}_mesh")
        obj = bpy.data.objects.new(f"{object_name}_mesh", mesh)
        
        # Create a new collection for object
        collection = bpy.data.collections.new(f"{object_name}_collection")
        bpy.context.scene.collection.children.link(collection)
        collection.objects.link(obj)
        
        bpy.context.view_layer.objects.active = obj
        bpy.context.active_object.select_set(True)
        
        bm = bmesh.new()
        
        # Create materials and add it to object slot
        for material in materials:
            matname = materials[material][0].decode('UTF-8').rstrip("\x00")
            if matname in bpy.data.materials:
                mat = bpy.data.materials[matname]
            else:
                mat = bpy.data.materials.new(matname)
                mat.use_nodes = True
            obj.data.materials.append(mat)
        
        # Dictionary for groups of vertices
        groups = {}
        
        # Create groups of vertices
        for link in bonelinks:
            group = bones[bonelinks[link][0]][0].decode('UTF-8').rstrip("\x00")
            if group not in groups:
                obj.vertex_groups.new(name = group)
                groups[group] = []
        
        # Create vertices
        for vertex in vertexes:
            try:
                pos = vertexes[vertex][0]
                bm.verts.new(positions[pos])
                
                # Add vertix to the dictionary for groups of vertices:
                groups[bones[bonelinks[pos][0]][0].decode('UTF-8').rstrip("\x00")].append(vertex)
            except ValueError:
                print(f"Can't create vertex {str(vertex)}")
        
        # Update vertices to get their indices
        bm.verts.ensure_lookup_table()
        bm.verts.index_update()
        
        # Create tris by links from vertex_tris
        for tris in vertex_tris:
            try:
                vn = vertex_tris[tris]
                fa = bm.faces.new([bm.verts[vn[0]], bm.verts[vn[1]], bm.verts[vn[2]]])
                fa.material_index = material_tris[tris][0]
            except ValueError:
                print(f"Can't create a {str(tris)} tri with vertixes {str(vertex_tris[tris])}!")
        
        # Add uv coordinates
        uv_layer = bm.loops.layers.uv.new()
        for face in bm.faces:
            for loop in face.loops:
                loop[uv_layer].uv.x = texcoords[vertexes[loop.vert.index][2]][0]
                loop[uv_layer].uv.y = 1 - texcoords[vertexes[loop.vert.index][2]][1]
        
        # Turn bmeh into mesh
        bm.to_mesh(mesh)  
        bm.free()
        
        # Add vertices to their groups
        for group in groups:
            obj.vertex_groups[group].add(groups[group], 1, 'ADD')
        
        # Go to Edit Vertices mode and split mesh into groups
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_mode(type = 'VERT')
        
        for vgroup in obj.vertex_groups:
            bpy.ops.mesh.select_all(action='DESELECT')
            
            # Select vertices group
            bpy.ops.object.vertex_group_set_active(group = vgroup.name)
            bpy.ops.object.vertex_group_select()
            
            # Using a comparison of a list of objects before and after splitting. Because the "separate" method does not return a new object
            objs = [ob for ob in bpy.data.objects if ob.type == 'MESH']
            bpy.ops.mesh.separate(type = 'SELECTED')
            objs = list(set([ob for ob in bpy.data.objects if ob.type == 'MESH']) - set(objs))
            
            # Select a new object, rename it, delete all extra vgroups, remove doubles and unused materials and recalculate normals
            newobj = objs[0]
            newobj.name = vgroup.name
            bpy.context.view_layer.objects.active = newobj
            vgroups = bpy.context.object.vertex_groups
            vgroups.active_index = vgroups[vgroup.name].index
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.object.vertex_group_select()
            bpy.ops.object.vertex_group_lock(action = 'LOCK', mask = 'SELECTED')
            bpy.ops.object.vertex_group_remove(all = False, all_unlocked = True)
            bpy.ops.mesh.remove_doubles()
            bpy.ops.mesh.normals_make_consistent(inside=False)                
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.material_slot_remove_unused()
            
            # Return to the main object
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.context.view_layer.objects.active = obj
        
        # Delete empty main object
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.ops.object.delete()
        
        # Create a new armature
        arm = bpy.data.armatures.new(object_name)
        rig = bpy.data.objects.new(object_name, arm)
        collection.objects.link(rig)
        context.view_layer.objects.active = rig
        bpy.ops.object.select_all(action = 'DESELECT')
        rig.select_set(True)
        bpy.context.view_layer.objects.active = rig
        
        # Create bones:
        for bone in bones:
            bpy.ops.object.mode_set(mode = 'EDIT')
            current_name = bones[bone][0].decode('UTF-8').rstrip("\x00")
            current_bone = arm.edit_bones.new(current_name)
            current_bone.head = [0, 0, 0]
            current_bone.tail = [0, 1, 0]

            # Add a child object to the bone
            try:
                rig.data.edit_bones.active = rig.data.edit_bones[current_name]
                bpy.ops.object.mode_set(mode = 'OBJECT')
                bpy.ops.object.select_all(action = 'DESELECT')
                bpy.data.objects[current_name].select_set(True)
                rig.select_set(True)
                bpy.context.view_layer.objects.active = rig
                bpy.ops.object.parent_set(type = 'BONE', keep_transform = True)
            except KeyError:
                print("Can't find the mesh for bone " + str(current_name))
                pass
            
            # Set bone pose with a quaternion
            bpy.ops.object.mode_set(mode = 'POSE')
            rig.pose.bones[current_name].matrix = [struct.unpack('<4f', bones[bone][2][:16]), 
                                                   struct.unpack('<4f', bones[bone][2][16:32]), 
                                                   struct.unpack('<4f', bones[bone][2][32:48]), 
                                                   struct.unpack('<4f', bones[bone][2][48:64])]
            
            # Attach bone to the parent
            bpy.ops.object.mode_set(mode = 'EDIT')
            current_bone = arm.edit_bones[current_name]
            parent_bone_name = bones[bone][1].decode('UTF-8').rstrip("\x00")
            try:
                parent_bone = arm.edit_bones[parent_bone_name]
                current_bone.parent = parent_bone
                current_bone.use_connect = False
            except KeyError:
                pass
        
        # Apply current pose as rest pose       
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action = 'DESELECT')        
        rig.select_set(True)
        context.view_layer.objects.active = rig
        bpy.ops.object.mode_set(mode = 'POSE')
        bpy.ops.pose.armature_apply(True)
        
        # Mirror armature and apply all transforms
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action = 'DESELECT')        
        rig.select_set(True)
        bpy.ops.transform.mirror(constraint_axis = [False, True, False])
        
        # Model loaded
        bpy.ops.object.select_all(action = 'DESELECT')
        print(f"Model '{file_name}' successfully imported")
        
        
    # Parse data chunk method
    def read_block(filedata, blockname, dictname, valuecount, valuetype):
            
        address = None
        
        # Try to find a chunk address
        try:
            address = filedata.index(blockname) + 64
        except ValueError:
            print(f"Chunk '{blockname.decode('UTF-8')}' is not found!")
            return
        
        # Get a chunk address
        address = struct.unpack('<I', filedata[address : address + 4])[0]
        
        # Read chunk size
        datasize = struct.unpack('<I', filedata[address : address + 4])[0]
        address += 4
        
        # Read data
        dataarray = []
        for datanumb in range(datasize):
            for data in range(valuecount):
                databyte = struct.unpack(valuetype[0], filedata[address : address + valuetype[1]])[0]
                dataarray.append(databyte)
                address += valuetype[1]
            dictname[datanumb] = dataarray.copy()
            dataarray.clear()
            if blockname == b'bones':
                # The bone element has an extra game data, we skip it
                address += 4 + int(struct.unpack('<I', filedata[address: address + 4])[0])


# Add plugin button into Blender import menu
def menu_func_import(self, context):
    self.layout.operator(ImportLMDL.bl_idname, text='Parkan II (.lmdl)')


# Plugin registration
def register():
    bpy.utils.register_class(ImportLMDL)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


# Plugin deregistration
def unregister():
    bpy.utils.unregister_class(ImportLMDL)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == '__main__':
    register()

