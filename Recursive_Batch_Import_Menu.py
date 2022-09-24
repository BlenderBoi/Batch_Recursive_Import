
import bpy


class BATCHIMPORT_MT_Recursive_Batch_Import_Menu(bpy.types.Menu):
    bl_label = "Recursive Batch Import"
    bl_idname = "BATCHIMPORT_MT_recursive_batch_import"

    def draw(self, context):
        layout = self.layout

        layout.operator("batch_import.recursive_import_fbx", text="FBX (.fbx)")
        layout.operator("batch_import.recursive_import_obj", text="Wavefront (.obj)")



def menu_func_import(self, context):
    self.layout.menu("BATCHIMPORT_MT_recursive_batch_import", text="Recursive Batch Import", icon="FILE_FOLDER")

# def menu_func_import(self, context):
#     self.layout.operator(BATCHIMPORT_OT_Recursive_Import_FBX.bl_idname, text="Recursive Batch Import (.fbx)")
#     self.layout.operator(BATCHIMPORT_OT_Recursive_Import_OBJ.bl_idname, text="Recursive Batch Import (.obj)")


classes = [BATCHIMPORT_MT_Recursive_Batch_Import_Menu]

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()


