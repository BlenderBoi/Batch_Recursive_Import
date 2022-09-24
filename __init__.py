
bl_info = {
    "name": "Batch Import",
    "author": "BlenderBoi",
    "version": (1, 0),
    "blender": (3, 00, 0),
    "description": "",
    "warning": "",
    "location": "File > Import",
    "wiki_url": "",
    "category": "Add Mesh",
}

import bpy
from . import Recursive_Batch_Import_OBJ


modules = [Recursive_Batch_Import_OBJ]

def register():

    for module in modules:
        module.register()

def unregister():

    for module in modules:
        module.unregister()

if __name__ == "__main__":
    register()
