
bl_info = {
    "name": "Batch Recursive Import",
    "author": "BlenderBoi",
    "version": (1, 1),
    "blender": (3, 00, 0),
    "description": "",
    "warning": "",
    "location": "File > Import",
    "wiki_url": "",
    "category": "Import-Export",
}

import bpy
from . import Recursive_Batch_Import_OBJ
from . import Recursive_Batch_Import_FBX
from . import Recursive_Batch_Import_Menu


modules = [Recursive_Batch_Import_OBJ, Recursive_Batch_Import_FBX, Recursive_Batch_Import_Menu]

def register():

    for module in modules:
        module.register()

def unregister():

    for module in modules:
        module.unregister()

if __name__ == "__main__":
    register()
