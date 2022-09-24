
import bpy

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

import pathlib
import os
import re

ENUM_Axis = [("X","X","X"),("Y","Y","Y"),("Z","Z","Z"),("NEGATIVE_X","-X","-X"),("NEGATIVE_Y","-Y","-Y"),("NEGATIVE_Z","-Z","-Z")]


def recursive_collect_file_by_format(root_directory, format):

    collected_files = []
    items = os.walk(root_directory)

    for (path, directories, files) in items:
        for file in files:
            if file.endswith(".obj"):
                collected_files.append(path+"/"+file)

    return collected_files



ENUM_Filter_Mode = [("INCLUDE","Include","Include"),("EXCLUDE","Exclude","Exclude"), ("REGEX", "Regex", "Regex")]

class BATCHIMPORT_OT_Recursive_Import_OBJ(Operator):
    """Recursive Import OBJ"""
    bl_idname = "batch_import.recursive_import_obj"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Batch Import OBJ"

    bl_options = {'UNDO', 'REGISTER'}
    # filename_ext = ".obj"
    # filename_ext = "."

    filter_glob: StringProperty(
        default="*.obj",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    directory: bpy.props.StringProperty()
    use_collection: bpy.props.BoolProperty(default=False, name="Use Collection")
    new_collection: bpy.props.BoolProperty(default=True, name="New Collection")
    collection_name: bpy.props.StringProperty(default="Import OBJ", name="Collection Name")
    file_name_as_collection: bpy.props.BoolProperty()

    filter_use: bpy.props.BoolProperty(default=False, name="Use Filter")
    filter_case_sensitive: bpy.props.BoolProperty(default=False, name="Case Sensitive")
    filter_text: bpy.props.StringProperty(name="Filter")
    filter_mode: bpy.props.EnumProperty(items=ENUM_Filter_Mode, name="Filter Mode")
    
    clamp_size: bpy.props.FloatProperty(default=0.0, min=0.0, name="Clamp Bounding")
    forward_axis: bpy.props.EnumProperty(default="X", items=ENUM_Axis, name="Axis Forward")
    up_axis: bpy.props.EnumProperty(default="Y", items=ENUM_Axis, name="Up")
    import_vertex_groups: bpy.props.BoolProperty(default=False, name="Vertex Groups")
    validate_meshes: bpy.props.BoolProperty(default=False, name="Validate Meshes")


    def invoke(self, context, event):

        if self.directory:
            self.collection_name = pathlib.Path(self.directory).stem
        else:
            self.collection_name = "Collection"

        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Batch Options", icon="MOD_ARRAY")

        box.label(text="Collection", icon="OUTLINER_COLLECTION")
        box.prop(self, "use_collection")
        if self.use_collection:
            row = box.row(align=True)
            if self.new_collection:
                row.prop(self, "collection_name", icon="OUTLINER_COLLECTION", text="")
            else:
                row.prop_search(self, "collection_name", bpy.data, "collections", icon="OUTLINER_COLLECTION", text="")

            row.prop(self, "new_collection", text="", icon="PLUS")
            box.prop(self, "file_name_as_collection", text="File Name As Collection", icon="CURRENT_FILE")

        box.separator()

        box.label(text="Filter", icon="FILTER")
        box.prop(self, "filter_use")

        if self.filter_use:
            col = box.column(align=True)
            row = col.row()
            row.prop(self, "filter_mode", expand=True)
            col.prop(self, "filter_text", text="", icon="FILTER")
            if self.filter_mode in ["INCLUDE", "EXCLUDE"]:
                box.prop(self, "filter_case_sensitive")


        box = layout.box()
        box.label(text="Transform", icon="OBJECT_DATA")

        box.prop(self, "clamp_size")
        box.prop(self, "forward_axis")
        box.prop(self, "up_axis")


        box = layout.box()
        box.label(text="Options", icon="EXPORT")
        box.prop(self, "import_vertex_groups")
        box.prop(self, "validate_meshes")

    def execute(self, context):




        files = recursive_collect_file_by_format(self.directory, ".obj")
        filtered_files = files

        original_objects = [object for object in bpy.data.objects]
        collection = None


        if self.filter_use:

            filtered_files = []


            for file in files:
                if self.filter_mode == "INCLUDE":

                    filename = os.path.basename(file)

                    if self.filter_case_sensitive:
                        if self.filter_text in filename:
                            filtered_files.append(file)
                    else:
                        if self.filter_text.lower() in filename.lower():
                            filtered_files.append(file)

                if self.filter_mode == "EXCLUDE":

                    if self.filter_case_sensitive:
                        if not self.filter_text in file:
                            filtered_files.append(file)
                    else:
                        if not self.filter_text.lower() in file.lower():
                            filtered_files.append(file)

                if self.filter_mode == "REGEX":
                    regex_match = bool(re.search(self.filter_text, file))
                    if regex_match:
                        filtered_files.append(file)




        self.report({"INFO"}, "Found " + str(len(filtered_files)) + " files ")
        print("Found " + str(len(filtered_files)) + " files")


        imported_files = {} 

        for object in context.selected_objects:
            object.select_set(False)


        if self.use_collection:
            if len(filtered_files) > 0:
                collection = create_collection(self.collection_name, not self.new_collection, context.collection)

        for file in filtered_files:

            # imported_files[file] = list(context.selected_objects)




            print("Importing " + file)
            self.report({"INFO"}, "Importing" + file)
            bpy.ops.wm.obj_import(filepath=file, clamp_size=self.clamp_size, forward_axis=self.forward_axis, up_axis=self.up_axis, import_vertex_groups=self.import_vertex_groups, validate_meshes=self.validate_meshes)

            imported_object = [obj for obj in bpy.data.objects if obj not in original_objects]
            imported_files[file] = imported_object

            original_objects = list(bpy.data.objects)


            if self.use_collection:

                if collection:
                    move_objects_to_collection(imported_object, collection)
            
                    if self.file_name_as_collection:
                        file_collection = create_collection(os.path.relpath(file, self.directory), True, collection)
                        move_objects_to_collection(imported_object, file_collection)





            

        print("-----")
        print("Imported Objects: ")
        for file in imported_files:
            print("-----")
            print("    " + file)
            for obj in imported_files[file]:
                print("        " + obj.name)




        


        return {"FINISHED"}


def move_to_collection(obj, collection):

    for col in obj.users_collection:
        col.objects.unlink(obj)

    collection.objects.link(obj)

def move_objects_to_collection(objs, collection):

    for obj in objs:
        move_to_collection(obj, collection)


def create_collection(name, use_exist, parent_collection):

    context = bpy.context
    collection = None
    isNew = True

    if use_exist:
        collection = bpy.data.collections.get(name)
        isNew = False

    if not collection:
        collection = bpy.data.collections.new(name)
        isNew = True

    
    if isNew:
        if not parent_collection.get(collection.name):
            parent_collection.children.link(collection)

    return collection





classes = [BATCHIMPORT_OT_Recursive_Import_OBJ]


def register():

    for cls in classes:
        bpy.utils.register_class(cls)


    # bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    # bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()




