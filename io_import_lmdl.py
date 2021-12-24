#Информация для плагина
bl_info = {
    'name': 'LMDL format',
    'author': 'RenViscoso',
    'version': (1, 0, 0),
    'blender': (2, 93, 0),
    'location': 'File > Import/Export',
    'description': 'Import LMDL files',
    'category': 'Import-Export',
}

#Импорт библиотек
import bpy
import bmesh
import struct
from bpy.props import (
    CollectionProperty,
    StringProperty,
    BoolProperty,
)
from bpy_extras.io_utils import ImportHelper

#Класс для выбора импортируемых файлов
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

    def execute(self, context):
        import os

        paths = [
            os.path.join(self.directory, name.name)
            for name in self.files
        ]

        if not paths:
            paths.append(self.filepath)

        for path in paths:
            ImportLMDL.lmdl_load(self, context, path)

        context.window.cursor_set('DEFAULT')

        return {'FINISHED'}

    #Функция для импорта 
    def lmdl_load(operator, context, filepath):

            #Чтение данных файла
            file = open(filepath, 'rb')
            filedata = file.read()
            file.close()
            
            #Проверка сигнатуры
            signature = filedata[0:9]
            if not signature.startswith(b'PII|BMDLT'):
                raise ValueError('Ошибка сигнатуры файла')
            
            #Типы данных, используемые в файле. Нужны для функции struct.unpack()
            datatypes = {
                'flt': ['<f', 4],
                'short': ['<H', 2],
                'string': ['64s', 64]
            }
            
            #Словари с данными
            positions = {}
            texcoords = {}
            vertexes = {}
            vertex_tris = {}
            materials = {}
            material_tris = {}
            bones = {}
            bonelinks = {}
            
            #Считываем данные в словари
            ImportLMDL.read_block(filedata, b'positions', positions, 3, datatypes['flt'])
            ImportLMDL.read_block(filedata, b'texcoords', texcoords, 2, datatypes['flt'])
            ImportLMDL.read_block(filedata, b'vertexes', vertexes, 6, datatypes['short'])
            ImportLMDL.read_block(filedata, b'vertex_tris', vertex_tris, 3, datatypes['short'])
            ImportLMDL.read_block(filedata, b'materials', materials, 1, datatypes['string'])
            ImportLMDL.read_block(filedata, b'material_tris', material_tris, 1, datatypes['short'])
            ImportLMDL.read_block(filedata, b'bonelinks', bonelinks, 1, datatypes['short'])
            ImportLMDL.read_block(filedata, b'bones', bones, 3, datatypes['string'])
            
            #Создаём новый mesh и объект на его основе
            mesh = bpy.data.meshes.new('mesh')
            obj = bpy.data.objects.new('NewObject', mesh)
            
            #Создаём новую коллекцию и привязываем объект к ней, чтобы избежать конфликтов
            #collection = bpy.context.collection 
            collection = bpy.data.collections.new('NewLMDL')    
            bpy.context.scene.collection.children.link(collection)
            collection.objects.link(obj)
            
            #Выбираем и активируем объект
            bpy.context.view_layer.objects.active = obj
            bpy.context.active_object.select_set(True)
            
            #Создаём новый bmesh
            bm = bmesh.new()
            
            #Создаём материалы, если они отсутствуют, и добавляем их в слоты объекта
            for material in materials:
                matname = materials[material][0].decode('UTF-8')
                if matname in bpy.data.materials:
                    mat = bpy.data.materials[matname]
                else:
                    mat = bpy.data.materials.new(matname)
                    mat.use_nodes = True
                obj.data.materials.append(mat)
            
            #Словарь для групп вершин
            groups = {}
            
            #Создаём группы вершин у объекта
            for link in bonelinks:
                group = bones[bonelinks[link][0]][0].decode('UTF-8')
                if group not in groups:
                    obj.vertex_groups.new(name = group)
                    groups[group] = []
            
            #Создаём вершины
            for vertex in vertexes:
                try:
                    pos = vertexes[vertex][0]
                    vt = bm.verts.new(positions[vertexes[vertex][0]])
                    groups[bones[bonelinks[pos][0]][0].decode('UTF-8')].append(vertex) #Добавляем вершину в словарь для групп вершин
                except ValueError:
                    print('Проблема при создании вершины ' + str(vertex)) #В случае ошибки в данных - пропускаем вершину
            
            #Обновляем вершины объектов, чтобы все они получили соответствующие индексы
            bm.verts.ensure_lookup_table()
            bm.verts.index_update()
            
            #Создаём грани
            for tris in vertex_tris:
                try:
                    vn = vertex_tris[tris]
                    fa = bm.faces.new([bm.verts[vn[0]], bm.verts[vn[1]], bm.verts[vn[2]]])
                    fa.material_index = material_tris[tris][0] #Назначаем материал для грани
                except ValueError:
                    print('Проблема при создании грани ' + str(tris) + ' с вершинами ' + str(vertex_tris[tris])) #В случае ошибки в данных - пропускаем грань
            
            #Создаём UV-координаты
            uv_layer = bm.loops.layers.uv.new()
            for face in bm.faces:
                for loop in face.loops:
                    loop[uv_layer].uv.x = texcoords[vertexes[loop.vert.index][2]][0]
                    loop[uv_layer].uv.y = 1 - texcoords[vertexes[loop.vert.index][2]][1]
            
            #Преобразуем bmesh в mesh
            bm.to_mesh(mesh)  
            bm.free()
            
            #Добавляем в группы вершин соответствующие вершины
            for group in groups:
                obj.vertex_groups[group].add(groups[group], 1, 'ADD')
            
            #Переходим в режим редактирования вершин
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_mode(type = 'VERT')
            
            for vgroup in obj.vertex_groups:
                bpy.ops.mesh.select_all(action='DESELECT') #Снимаем выделение
                
                #Выбираем группу вершин:
                bpy.ops.object.vertex_group_set_active(group = vgroup.name)
                bpy.ops.object.vertex_group_select()
                
                objs = [ob for ob in bpy.data.objects if ob.type == 'MESH'] #Сохраняем список объектов
                bpy.ops.mesh.separate(type = 'SELECTED') #Отделяем группу вершин, создавая новый объект
                objs = list(set([ob for ob in bpy.data.objects if ob.type == 'MESH']) - set(objs)) #Ещё раз сохраняем список объектов и удаляем из него старый. Оставшийся объект - только что созданный нами
                
                #Выбираем новый объект, даём ему имя как у группы вершин, очищаем список групп вершин, спаиваем вершины, оказавшиеся в одной точке, устанавливаем сглаживание и удаляем неиспользованные слоты с материалами:
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
                bpy.ops.object.shade_smooth()
                bpy.ops.object.material_slot_remove_unused()
                
                #Возвращаемся к первичному объекту
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.context.view_layer.objects.active = obj
            
            #Выбираем оставшийся пустым первичный объект и удаляем его
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.ops.object.delete()
            
            #Создаём новый armature и привязываем его к новому объекту, а тот - к текущей коллекции. Выбираем объект с armature
            arm = bpy.data.armatures.new('Armature')
            rig = bpy.data.objects.new('Armature', arm)
            collection.objects.link(rig)
            context.view_layer.objects.active = rig
            bpy.ops.object.select_all(action = 'DESELECT')
            rig.select_set(True)
            bpy.context.view_layer.objects.active = rig
            
            #Создаём кости в armature:
            for bone in bones:
                #Переходим в режим редактирования и создаём новую кость
                bpy.ops.object.mode_set(mode = 'EDIT')
                current_name = bones[bone][0].decode('UTF-8')
                current_bone = arm.edit_bones.new(current_name)
                current_bone.head = [0, 0, 0]
                current_bone.tail = [0, 1, 0]

                #Привязываем соответствующий объект к кости, добавляем к имени объекта "_mesh" для избежания конфликтов
                try:
                    rig.data.edit_bones.active = rig.data.edit_bones[current_name]
                    bpy.ops.object.mode_set(mode = 'OBJECT')
                    bpy.ops.object.select_all(action = 'DESELECT')
                    bpy.data.objects[current_name].select_set(True)
                    rig.select_set(True)
                    bpy.context.view_layer.objects.active = rig
                    bpy.ops.object.parent_set(type = 'BONE', keep_transform = True)
                    bpy.data.objects[current_name].name += '_mesh'
                except KeyError:
                    print('Не найден меш для кости ' + str(current_name))
                    pass #В случае любой ошибки - идём дальше
                
                #Переходим в режим позы и задаём положение для кости с помощью кватерниона
                bpy.ops.object.mode_set(mode = 'POSE')
                rig.pose.bones[current_name].matrix = [struct.unpack('<4f', bones[bone][2][:16]), struct.unpack('<4f', bones[bone][2][16:32]), struct.unpack('<4f', bones[bone][2][32:48]), struct.unpack('<4f', bones[bone][2][48:64])]
                bpy.ops.object.mode_set(mode = 'EDIT')
                
                #Привязываем кость к родительской кости
                current_bone = arm.edit_bones[current_name]
                parent_bone = bones[bone][1].decode('UTF-8')
                try:
                    current_bone.parent = arm.edit_bones[parent_bone]
                    current_bone.use_connect = False
                except KeyError:
                    pass #В случае любой ошибки - идём дальше
            
            #Применяем текущую позу как rest pose:       
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.select_all(action = 'DESELECT')        
            rig.select_set(True)
            context.view_layer.objects.active = rig
            bpy.ops.object.mode_set(mode = 'POSE')
            bpy.ops.pose.armature_apply(True)   
            
            #Переключаемся обратно в режим объекта и выводим сообщение о загрузившейся модели:
            bpy.ops.object.mode_set(mode = 'OBJECT')
            print('Модель "' + filepath + '" загружена')

    #Функция чтения блока данных
    def read_block(filedata, blockname, dictname, valuecount, valuetype):
            #Поиск адреса блока. В случае его отсутствия пишем об этом в консоль и идём дальше
            try:
                adress = filedata.index(blockname) + 64
            except ValueError:
                print('Блок ' + blockname.decode('UTF-8') + ' не найден')
                return
            
            #Считываем адрес блока в файле
            adress = struct.unpack('<I', filedata[adress : adress + 4])[0]
            
            #Считываем размер блока данных
            datasize = struct.unpack('<I', filedata[adress : adress + 4])[0]
            adress += 4
            
            #Считываем данные в виде байтов в массив
            dataarray = []
            for datanumb in range(datasize):
                for data in range(valuecount):
                    databyte = struct.unpack(valuetype[0], filedata[adress : adress + valuetype[1]])[0]
                    dataarray.append(databyte)
                    adress += valuetype[1]
                dictname[datanumb] = dataarray.copy() #Выводим данные в элемент словаря
                dataarray.clear()
                if blockname == b'bones':
                    #У блока bones после описания кости идут дополнительные данные для игры. Пропускаем их
                    adress += 4 + int(struct.unpack('<I', filedata[adress: adress + 4])[0])
    
#Добавление кнопки вызова плагина в меню импорта Blender
def menu_func_import(self, context):
    self.layout.operator(ImportLMDL.bl_idname, text='Parkan II (.lmdl)')

#Регистрация плагина при его подключении
def register():
    bpy.utils.register_class(ImportLMDL)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

#Дерегистрация плагина при его отключении
def unregister():
    bpy.utils.unregister_class(ImportLMDL)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == '__main__':
    register()
