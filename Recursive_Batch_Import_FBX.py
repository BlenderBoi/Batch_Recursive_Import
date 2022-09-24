

import bpy
import bpy_extras
from bpy_extras.io_utils import orientation_helper
from . import Utility_Function

import os
import pathlib
import webbrowser
import re



ENUM_fbx_manual_orientation_up=[("","",""),("","",""),("","",""),("","",""),("","",""),("","","")]
ENUM_fbx_manual_orientation_forward=[("","",""),("","",""),("","",""),("","",""),("","",""),("","","")]
ENUM_bone_axis=[("X","X Axis",""),("Y","Y Axis",""),("Z","Z Axis",""),("-X","-X Axis",""),("-Y","-Y Axis",""),("-Z","-Z Axis","")]

# ENUM_Load_To=[("ACTIVE","Active Object","Active Object"),("DETECT_NAME","Detect Object Name","Detect Object Name"), ("NONE", "None", "None")]
# ENUM_Load_To=[("ACTIVE","Active Object","Active Object"), ("NONE", "None", "None")]

ENUM_Filter_Mode = [("INCLUDE","Include","Include"),("EXCLUDE","Exclude","Exclude"), ("REGEX", "Regex", "Regex")]



def recursive_collect_file_by_format(root_directory, format):

    collected_files = []
    items = os.walk(root_directory)

    for (path, directories, files) in items:
        for file in files:
            if file.endswith(format):
                collected_files.append(path+"/"+file)

    return collected_files



@orientation_helper(axis_forward='-Z', axis_up='Y')
class BATCHIMPORT_OT_Recursive_Import_FBX(bpy.types.Operator):
    """Recursive Import FBX"""
    bl_idname = "batch_import.recursive_import_fbx"
    bl_label = "Batch Import FBX"
    bl_options = {'UNDO', 'REGISTER', 'PRESET'}


    directory: bpy.props.StringProperty()
    use_collection: bpy.props.BoolProperty(default=False, name="Use Collection")
    new_collection: bpy.props.BoolProperty(default=True, name="New Collection")
    collection_name: bpy.props.StringProperty(default="Import FBX", name="Collection Name")
    file_name_as_collection: bpy.props.BoolProperty()

    filter_use: bpy.props.BoolProperty(default=False, name="Use Filter")
    filter_case_sensitive: bpy.props.BoolProperty(default=False, name="Case Sensitive")
    filter_text: bpy.props.StringProperty(name="Filter")
    filter_mode: bpy.props.EnumProperty(items=ENUM_Filter_Mode, name="Filter Mode")


    # filename_ext = ".fbx"
    filter_glob: bpy.props.StringProperty(
        default="*.fbx", 
        options={'HIDDEN'}
    )
    



    
    fbx_transform_scale: bpy.props.FloatProperty(
        default=1.0, 
        min=0
    )


    fbx_decal_offset: bpy.props.FloatProperty(
            name="Decal Offset",
            description="Displace geometry of alpha meshes",
            min=0.0, max=1.0,
            default=0.0,
            )


    fbx_use_custom_normals: bpy.props.BoolProperty(
            name="Custom Normals",
            description="Import custom normals, if available (otherwise Blender will recompute them)",
            default=True,
            )


    fbx_use_subsurf: bpy.props.BoolProperty(
            name="Subdivision Data",
            description="Import FBX subdivision information as subdivision surface modifiers",
            default=False,
            )


    fbx_use_custom_props: bpy.props.BoolProperty(
            name="Custom Properties",
            description="Import user properties as custom properties",
            default=True,
            )
    fbx_use_custom_props_enum_as_string: bpy.props.BoolProperty(
            name="Import Enums As Strings",
            description="Store enumeration values as strings",
            default=True,
            )

    fbx_use_image_search: bpy.props.BoolProperty(
            name="Image Search",
            description="Search subdirs for any associated images (WARNING: may be slow)",
            default=True,
            )








    fbx_transform_apply_transform: bpy.props.BoolProperty(
        default=False,
        description="Bake space transform into object data, avoids getting unwanted rotations to objects when "
                    "target space is not aligned with Blender's space "
                    "(WARNING! experimental option, use at own risks, known broken with armatures/animations)",
    )

    fbx_transform_pre_post_rotation: bpy.props.BoolProperty(
        default=True,
        description="Use pre/post rotation from FBX transform (you may have to disable that in some cases)",
    ) 
    
    fbx_manual_orientation: bpy.props.BoolProperty(
        default=False,
        description="Specify orientation and scale, instead of using embedded data in FBX file",
    )
    # fbx_manual_orientation_forward: bpy.props.EnumProperty(items=ENUM_fbx_manual_orientation_forward)
    # fbx_manual_orientation_up: bpy.props.EnumProperty(items=ENUM_fbx_manual_orientation_up)

    fbx_animation_offset: bpy.props.FloatProperty(
        default=1.0, 
        description="Offset to apply to animation during import, in frames",
    )

    fbx_armature_ignore_leaf_bone: bpy.props.BoolProperty(
        default=False,
        description="Ignore the last bone at the end of each chain (used to mark the length of the previous bone)",
    )

    fbx_armature_force_connect_child: bpy.props.BoolProperty(
        default=False,
        description="Force connection of children bones to their parent, even if their computed head/tail "
                    "positions do not match (can be useful with pure-joints-type armatures)",
    )

    fbx_armature_automatic_bone_orientation: bpy.props.BoolProperty(
        default=False,
        description="Try to align the major bone axis with the bone children",
    )

    fbx_armature_primary_bone_axis: bpy.props.EnumProperty(
        items=ENUM_bone_axis, 
        default="Y"
    )

    fbx_armature_secondary_bone_axis: bpy.props.EnumProperty(
        items=ENUM_bone_axis,                           
        default="X"
    )


    def invoke(self, context, event):

        if self.directory:
            self.collection_name = pathlib.Path(self.directory).stem
        else:
            self.collection_name = "Collection"

        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def draw_builtin_fbx_options(self, context, layout):

        layout.label(text="Include") 
        box = layout.box()
        box.prop(self, "fbx_use_custom_normals", text="Custom Normals")
        box.prop(self, "fbx_use_subsurf", text="Subdivision Data")
        box.prop(self, "fbx_use_custom_props", text="Custom Properties")
        box.prop(self, "fbx_use_custom_props_enum_as_string", text="Import Enums As String")
        box.prop(self, "fbx_use_image_search", text="Image Search")



        layout.label(text="Transform") 
        box = layout.box()
        box.prop(self, "fbx_transform_scale", text="Scale")
        box.prop(self, "fbx_decal_offset", text="Decal Offset")
        row = box.row()
        row.prop(self, "fbx_transform_apply_transform", text="Apply Transform")
        row.label(text="Experimental", icon="ERROR")

        box.prop(self, "fbx_transform_pre_post_rotation", text="Use Pre/Post Rotation")
        
        box.prop(self, "fbx_manual_orientation", text="Manual Orientation")

        sub_box = box.box()
        sub_box.enabled = self.fbx_manual_orientation
        sub_box.prop(self, "axis_forward", text="Forward")

        sub_box.prop(self, "axis_up", text="Up")


        layout.label(text="Animation")
        box = layout.box()
        box.prop(self, "fbx_animation_offset", text="Animation Offset")


        layout.label(text="Armature")
        box = layout.box()

        box.label(text="Primary Bone Axis:")
        box.prop(self, "fbx_armature_primary_bone_axis", text="")

        box.label(text="Secondary Bone Axis:")
        box.prop(self, "fbx_armature_secondary_bone_axis", text="")


        box.prop(self, "fbx_armature_ignore_leaf_bone", text="Ignore Leaf Bone")
        box.prop(self, "fbx_armature_force_connect_child", text="Force Connect Child")
        box.prop(self, "fbx_armature_automatic_bone_orientation", text="Automatic Bone Orientation")


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


        self.draw_builtin_fbx_options(context, layout)

    def execute(self, context):




        files = recursive_collect_file_by_format(self.directory, ".fbx")
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
            # bpy.ops.wm.obj_import(filepath=file, clamp_size=self.clamp_size, forward_axis=self.forward_axis, up_axis=self.up_axis, import_vertex_groups=self.import_vertex_groups, validate_meshes=self.validate_meshes)

            bpy.ops.import_scene.fbx(
                filepath=file, 
                use_custom_normals=self.fbx_use_custom_normals,
                use_subsurf=self.fbx_use_subsurf,
                use_custom_props=self.fbx_use_custom_props,
                use_custom_props_enum_as_string=self.fbx_use_custom_props_enum_as_string,
                use_image_search=self.fbx_use_image_search,
                global_scale=self.fbx_transform_scale,
                decal_offset=self.fbx_decal_offset,
                bake_space_transform=self.fbx_transform_apply_transform,
                use_prepost_rot=self.fbx_transform_pre_post_rotation,
                use_manual_orientation=self.fbx_manual_orientation,
                axis_forward=self.axis_forward,
                axis_up=self.axis_up,
                use_anim=True, 
                anim_offset=self.fbx_animation_offset,
                ignore_leaf_bones=self.fbx_armature_ignore_leaf_bone,
                force_connect_children=self.fbx_armature_force_connect_child,
                automatic_bone_orientation=self.fbx_armature_automatic_bone_orientation,
                primary_bone_axis=self.fbx_armature_primary_bone_axis,
                secondary_bone_axis=self.fbx_armature_secondary_bone_axis
            ) 








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




classes = [BATCHIMPORT_OT_Recursive_Import_FBX]


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
