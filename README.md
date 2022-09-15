[Для русскоговорящих](#для-русскоговорящих)

# For English speakers

## Contents
1. [Apologies](#apologies)
2. [General disclaimer](#general-disclaimer)
3. [Description](#description)
4. [Setup](#setup)
5. [Manual](#manual)
6. [Materials and textures](#materials-and-textures)

## Apologies
Unfortunately, my English is not the best, and therefore there may be oddities in the text.
I apologize in advance for the inconvenience caused and will gladly accept your help to improve the English manual.

[:arrow_up_small:To the Contents](#contents)

## General disclaimer
This program is intended to be used for entertainment purposes and purposes of examination of resources available in the "Parkan 2" game only.

All rights to the models exported with this plug-in and the rights to the "Parkan 2" game belong to Nikita. The author only owns the copyright for this program.

The author of the program is not responsible for the actions of users of this program and does not aim to receive any material profit from its creation, support and use.

**If you have any questions related to my possible violation of a license right, please first contact me at: renviscoso@mail.ru**

[:arrow_up_small:To the Contents](#contents)

## Description
LMDL-Loader plugin for Blender *2.9+*.

This plugin allows you to load models from Parkan 2 into Blender (animations not included).

[:arrow_up_small:To the Contents](#contents)

## Setup
**Edit** - **Preferences** - **Add-ons** - **Install** button - Select plugin file - Activate the plugin in the list (you may need to search for **lmdl format**)

[:arrow_up_small:To the Contents](#contents)

## Manual
After activation, you can find in the **File** - **Import** list a new line **Parkan II (.lmdl)**.

Click on it and select the desired model file.

The model files are divided into semantic groups, whether they are **ship**, **bot**, **droid**, etc. Models names, unfortunately, are too short, but they should help you recognize which model you are importing if you're familiar with the game.

After importing, it is recommended to mirror the model armature along the Y axis (for some reason they are written like this, this can be found in the early screenshots of the game). If you later decide to unparent the meshes from the skeleton, do so via **Clear Parent and Keep Transformation**

<details>
<summary>Mirroring on an early screenshot</summary>
![Mirroring on an early screenshot](http://parkanfans.narod.ru/screenshots/p2/p2screen0058.jpg)

> The Captain's rifle is on the left in this early screenshot.
</details>

[:arrow_up_small:To the Contents](#contents)

## Materials and textures
To apply textures to models, you will need decompiled lua scripts. You can find them on this site: http://parkanfans.narod.ru/p2/files.htm

First you should download **ParkanScripts.rar** and unzip it to any folder, then download **lmtr.rar** and unzip it there with file replacement.

In Blender, in the **Shading** panel, you can find named material slots for model elements. To apply the material, you will need to find a file with the same name among the scripts in the **lmtr** folder. Inside will be specified textures that can be found in the **texture** folder in the root directory of the game, as well as various flags for materials.

The **diffuse map** of the model must be specified in the **diffusemap{texname}** parameter. The **bumpmap{texname}** parameter specifies the name of the **normal map** and is **optional**.

If you see a file with the **.ifl** extension as a texture, then you should not be afraid: these files are opened with a simple Notepad and contain a list of textures for different clans. But I want to note that **.ifl files** are randomly located either in the **texture** folder or in the **lmtr** folder. Apparently, the developers themselves have not decided what they can be classified.

Material flags can be listed in the flags{} parameter and are also **optional**.

The absence of flags means that you can simply apply textures (don't forget to **invert the normal map G channel (1 - x)**).

With the presence of flags, everything becomes a little more complicated, because in order to tell exactly which flag is responsible for what, you will have to explore many of the game's shaders (the **shaders** folder). But one of the most common flags is called **"selfillume"**.

The **"selfillume"** flag requires you to take the diffuse map alpha channel, invert it **(1 - x)** and attach it to the **Emission Strenght** input. RGB channels are connected to the **Emission** input, as well as to the **Base Color** input.

The **"twosided"** flag is self-explanatory and requires the material to be two-sided.

You will have to set the purpose of all other flags either by experience or by exploring the shader codes. I would be very happy if you share your research results with me so that I can catalog them here.

<details>
<summary>Examples of working with materials and textures</summary>
![The name of the material is in a red frame](https://user-images.githubusercontent.com/90441521/190520063-9eddbbfd-8d04-4585-b51c-8d1eef0c3503.png)

> The name of the material is in a red frame

![The required material is in the lmtr folder](https://user-images.githubusercontent.com/90441521/190520065-c9254177-61a5-42d9-82c2-bdda8f203bd2.png)

> The required material is in the **lmtr** folder

![Material data](https://user-images.githubusercontent.com/90441521/190520067-e8828ec6-bfe3-42c0-8515-8ba329ae7eda.png)

> The **diffuse map** is in the red frame. (By the way, it refers to the **.ifl** format).
> The **normal map** is in the purple frame. (It's common .dds).
> The **"selfillume"** flag is in the green frame.

![Textures](https://user-images.githubusercontent.com/90441521/190520055-70251816-64ce-4312-b777-eb97c5e2e94a.png)

> Texture files. Red is **diffuse map**, purple is **normal map**.

![.ifl data](https://user-images.githubusercontent.com/90441521/190520057-1bb7ba17-886b-4575-97fb-6fa7855d305d.png)

> Contents of **.ifl-file**. Here are textures for different clans. You can find all these files in the **texture** folder.


![Final material](https://user-images.githubusercontent.com/90441521/190520058-42c9e9ff-d4cb-4758-89b1-a731c2c797cf.png)

> Final material for **"selfillume"** flag.
> If this flag is missing, just remove the emission.
</details>

[:arrow_up_small:To the Contents](#contents)

____

# Для русскоговорящих

## Содержание
1. [Отказ от ответственности](#отказ-от-ответственности)
2. [Описание](#описание)
3. [Установка](#установка)
4. [Руководство по плагину](#руководство-по-плагину)
5. [Материалы и текстуры](#материалы-и-текстуры)

## Отказ от ответственности
Данная программа предназначена исключительно для использования в развлекательных целях, а также для рассмотрения доступного в игре "Parkan 2" контента.

Все права на импортируемые данным плагином модели, ровно как и на игру "Parkan 2", принадлежат компании Nikita. Автору принадлежит лишь авторское право на данную программу.

Автор программы не несёт ответственности за действия пользователей данной программы и не имеет цели получать с её создания, поддержки и использования какую-либо материальную прибыль.

В случае возникновения любых вопросов, связанных с возможным нарушением мною лицензионного права, пожалуйста, сначала свяжитесь со мной по адресу: renviscoso@mail.ru

[:arrow_up_small:К Содержанию](#содержание)

## Описание
Плагин для загрузки LMDL-моделей для Blender версии **2.9+**
Данный плагин позволяет загружать модели из игры Parkan 2 в Blender (к сожалению, пока без анимаций)

[:arrow_up_small:К Содержанию](#содержание)

## Установка
**Edit** - **Preferences** - **Add-ons** - кнопка **Install** - Выбрать файл плагина - Активировать плагин в списке (может понадобиться вбить в поиск **lmdl format**)

[:arrow_up_small:К Содержанию](#содержание)

## Руководство по плагину.
После активации Вы можете обнаружить в списке **Файл** — **Импорт** новую строку **Parkan II (.lmdl)**.

Нажмите на неё и выберите нужный файл модели.

Файлы модели распределены по смысловым группам, будь то **ship** (корабли), **bot** (варботы), **droid** (дроиды и космодесантники) и др. Названия моделей, к сожалению, очень краткие, но должны помочь Вам распознать, какую именно модель Вы импортируете, если Вы знакомы с игрой.

После загрузки рекомендуется отразить скелет модели по оси Y (по какой-то причине они записаны так, это можно найти на ранних скриншотах игры). Если впоследствии Вы решите отвязать меши от скелета, делайте это через пункт **Clear Parent and Keep Transformation**

<details>
<summary>Отражение на раннем скриншоте</summary>
![Отражение на раннем скриншоте](http://parkanfans.narod.ru/screenshots/p2/p2screen0058.jpg)

> Винтовка Капитана на этом раннем скриншоте находится слева.
</details>

[:arrow_up_small:К Содержанию](#содержание)

## Материалы и текстуры
Для применения текстур к моделям Вам понадобятся декомпилированные lua-скрипты. Найти их Вы можете на этом сайте: http://parkanfans.narod.ru/p2/files.htm

Сначала Вам следует скачать **ParkanScripts.rar** и разархивировать его в любую папку, затем скачать **lmtr.rar** и разархивировать его туда же с заменой файлов.

В Blender на панели **Shading** вы можете обнаружить у элементов модели именованные слоты для материалов. Для применения материала Вам необходимо будет найти среди скриптов в папке **lmtr** файл с таким же названием. Внутри будут указаны текстуры, которые можно найти в папке texture в корневой директории игры, а также различные флаги для материалов.

**Основная текстура** модели должна быть указана в параметре **diffusemap{texname}**. Параметр **bumpmap{texname}** указывает на название **карты нормалей** и необязателен.

В случае, если в качестве текстуры Вы видите файл с расширением **.ifl**, то не стоит пугаться: эти файлы открываются простым блокнотом и содержат список текстур для разных кланов. Но хочу обратить внимание, что файлы с этим расширением случанйым образом находятся либо в папке **texture**, либо в папке **lmtr**. Видимо, разработчики сами не решили, к чему их можно отнести.

Флаги материала могут быть перечислены в параметре **flags{}**.

Отсутствие флагов означает, что Вы можете просто применить текстуры (не забудьте **инвертировать (1 - x) канал G у карты нормалей**).

С наличием флагов всё становится немного сложнее, ведь чтобы точно сказать, какой флаг за что отвечает, придётся провести изучение множества шейдеров игры (папка **shaders**). Но один из самых частых флагов называется "selfillume". 

Флаг "selfillume" требует, чтобы Вы взяли альфа-канал diffusemap, инвертировали его **(1 - x)** и присоединили ко входу "Emission Strenght". Ко входу "Emission", как и ко входу "Base Color", присоединяются каналы RGB.

Флаг "twosided" говорит сам за себя и требует, чтобы материал был двусторонним.

Назначение всех остальных флагов вам придётся установить либо опытным путём, либо изучив коды шейдеров. Буду очень рад, если вы поделитесь со мной результатами своих исследований, чтобы я мог составить их каталог здесь.

<details>
<summary>Примеры работы с материалами и текстурами</summary>
![Имя материала указано в красной рамке](https://user-images.githubusercontent.com/90441521/190520063-9eddbbfd-8d04-4585-b51c-8d1eef0c3503.png)

> Имя материала указано в красной рамке

![Нужный материал в папке lmtr](https://user-images.githubusercontent.com/90441521/190520065-c9254177-61a5-42d9-82c2-bdda8f203bd2.png)

> Нужный материал в папке **lmtr**

![Данные материала](https://user-images.githubusercontent.com/90441521/190520067-e8828ec6-bfe3-42c0-8515-8ba329ae7eda.png)

> В красной рамке указана **основная текстура** (кстати, она ссылается на формат **.ifl**).
> В фиолетовой рамке указана **карта нормалей** (стандартный .dds).
> В зелёной рамке указан флаг **"selfillume"**.

![Файлы текстур](https://user-images.githubusercontent.com/90441521/190520055-70251816-64ce-4312-b777-eb97c5e2e94a.png)

> Файлы текстур. Красная — **основная**, фиолетовая — **карта нормалей**.

![Содержимое .ifl](https://user-images.githubusercontent.com/90441521/190520057-1bb7ba17-886b-4575-97fb-6fa7855d305d.png)

> Содержимое **.ifl-файла**. Здесь перечислены текстуры для разных кланов. **Вы можете найти все эти файлы в папке texture**.


![Итоговый материал](https://user-images.githubusercontent.com/90441521/190520058-42c9e9ff-d4cb-4758-89b1-a731c2c797cf.png)

> Итоговый материал для флага **"selfillume"**.
> Если этого флага не будет — просто уберите свечение.
</details>

[:arrow_up_small:К Содержанию](#содержание)
