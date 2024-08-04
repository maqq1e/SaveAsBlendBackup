import bpy
from bpy.props import StringProperty
import os


# Addon Info
bl_info = {
    "name": "Save as Backup",
    "author": "https://github.com/maqq1e",
    "description": "Easy and fast save separate objects and collection as backup .blend files",
    "blender": (3, 6, 0),
    "version": (1, 2, 0),
}

# Preferences Panel 
class CubeCreatorSaverPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    save_file_name: StringProperty(
        name="Backup Folder Path",
        description="NAme of folder to backup files",
        default="Backups",
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "save_file_name")

# Additional functions
def create_unique_path(context, name, directory):

    # Get the file name from the addon preferences
    preferences = context.preferences.addons[__name__].preferences
    file_name = preferences.save_file_name
    
    blendname = bpy.data.filepath[bpy.data.filepath.rfind('\\') + 1:-6]

    isFileExist = True

    number = 1

    while isFileExist:
        
        # Set the filename for the backup
        backup_filename = f"{file_name}/{blendname} - {name} {number}.blend"

        backup_filepath = os.path.join(directory, backup_filename)

        if os.path.exists(backup_filepath):
            number += 1
            isFileExist = True
        else:
            return backup_filepath
        
def delete_unused_data():
    bpy.data.orphans_purge()
        
def move_objects_to_collection(objects, target_collection_name):
    # Ensure the target collection exists
    if target_collection_name not in bpy.data.collections:
        target_collection = bpy.data.collections.new(target_collection_name)
        bpy.context.scene.collection.children.link(target_collection)
    else:
        target_collection = bpy.data.collections[target_collection_name]

    # Iterate through all objects in the scene
    for obj in objects:
        # Skip objects already in the target collection
        if target_collection_name in [col.name for col in obj.users_collection]:
            continue

        # Remove the object from all other collections
        for col in obj.users_collection:
            col.objects.unlink(obj)
        
        # Add the object to the target collection
        target_collection.objects.link(obj)
    
    return target_collection

# Main functions

def save_backup_WRAP(context, func, data):
    bpy.ops.wm.save_mainfile()

    # Get the current blend file path
    blend_filepath = bpy.data.filepath
    if not blend_filepath:
        print("Save the .blend file first.")
        return

    # Get the directory of the current blend file
    directory = os.path.dirname(blend_filepath)

    # Get the file name from the addon preferences
    preferences = context.preferences.addons[__name__].preferences
    file_name = preferences.save_file_name
    
    # Create path
    if not os.path.exists(directory + "\\" + file_name):
        os.makedirs(directory + "\\" + file_name)

    backup_filepath = func(context, data, directory)    
    
    delete_unused_data()

    # Create a new blend file for the backup
    bpy.ops.wm.save_as_mainfile(filepath=backup_filepath, copy=True)
    
    # Reopen the original blend file
    bpy.ops.wm.open_mainfile(filepath=blend_filepath)

def save_collection_backup(context, collection, directory):

    unique_path = create_unique_path(context, collection.name, directory)

    new_collection_name = 'Backup - ' + collection.name
        
    new_collection = move_objects_to_collection(collection.objects, new_collection_name)

    # Deselect all collections
    for coll in bpy.data.collections:
        coll.hide_viewport = True

    # Select only the target collection
    new_collection.hide_viewport = False
    
    # Remove all collections except the selected one
    for coll in bpy.data.collections:
        if coll != new_collection:
            bpy.data.collections.remove(coll)

    return unique_path

def save_selected_objects_backup(context, objects, directory):

    unique_path = create_unique_path(context, objects[0].name, directory)

    new_collection_name = 'Backup - ' + objects[0].name

    new_collection = move_objects_to_collection(objects, new_collection_name)

    # Deselect all collections
    for coll in bpy.data.collections:
        coll.hide_viewport = True

    # Select only the target collection
    new_collection.hide_viewport = False
    
    # Remove all collections except the selected one
    for coll in bpy.data.collections:
        if coll != new_collection:
            bpy.data.collections.remove(coll)

    return unique_path

# Operator for saving collection backup
class OBJECT_OT_save_collection_backup(bpy.types.Operator):
    '''Save selected collection as separate .blend file'''
    bl_idname = "object.save_collection_backup"
    bl_label = "Save Backup"
    
    collection_name: bpy.props.StringProperty()
    
    def execute(self, context):
        if bpy.data.is_saved:
            collection = bpy.data.collections.get(self.collection_name)
            if collection:
                save_backup_WRAP(context, save_collection_backup, collection)
                self.report({'INFO'}, f"Backup saved.")
            else:
                self.report({'ERROR'}, f"Collection not found")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, f"You need to save you .blend file!")
            return {'FINISHED'}

# Operator for saving selected objects backup
class OBJECT_OT_save_selected_objects_backup(bpy.types.Operator):
    '''Save selected objects as separate .blend file'''
    bl_idname = "object.save_selected_objects_backup"
    bl_label = "Save Backup"
    
    def execute(self, context):
        if bpy.data.is_saved:
            if context.selected_objects:
                save_backup_WRAP(context, save_selected_objects_backup, context.selected_objects)
                self.report({'INFO'}, "Backup saved for selected objects")
            else:
                self.report({'ERROR'}, "No objects selected")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, f"You need to save you .blend file!")
            return {'FINISHED'}

# Menu entry for the context menu
def collection_func(self, context):
    layout = self.layout
    selected_collection = context.collection
    if selected_collection:
        layout.operator(OBJECT_OT_save_collection_backup.bl_idname, text="Save Backup").collection_name = selected_collection.name

def object_func(self, context):
    layout = self.layout
    selected_object = context.selected_objects
    
    layout.operator(OBJECT_OT_save_selected_objects_backup.bl_idname, text="Save Backup").selected_objects = selected_object

# Registering the operator and menu
def register():
    bpy.utils.register_class(OBJECT_OT_save_collection_backup)
    bpy.utils.register_class(OBJECT_OT_save_selected_objects_backup)
    bpy.utils.register_class(CubeCreatorSaverPreferences)
    bpy.types.OUTLINER_MT_collection.append(collection_func)
    bpy.types.OUTLINER_MT_object.append(object_func)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_save_collection_backup)
    bpy.utils.unregister_class(OBJECT_OT_save_selected_objects_backup)
    bpy.utils.unregister_class(CubeCreatorSaverPreferences)
    bpy.types.OUTLINER_MT_collection.remove(collection_func)
    bpy.types.OUTLINER_MT_object.remove(object_func)

if __name__ == "__main__":
    register()
