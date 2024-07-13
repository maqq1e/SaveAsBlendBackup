import bpy
import os


# Addon Info
bl_info = {
    "name": "Save as Backup",
    "author": "https://github.com/maqq1e",
    "description": "Easy and fast save sepearet objects and collection as backup .blend files",
    "blender": (4, 0, 0),
    "version": (0, 1, 0),
}

def create_unique_path(collection, directory):
    
    isFileExist = True

    number = 1

    while isFileExist:
        
        # Set the filename for the backup
        backup_filename = f"Backups/{collection.name} {number}.blend"

        backup_filepath = os.path.join(directory, backup_filename)

        if os.path.exists(backup_filepath):
            number += 1
            isFileExist = True
        else:
            return backup_filepath
        

def move_objects_from_collection(collection_from, collection_to):
    # Ensure the collection exists
    if collection_from not in bpy.data.collections:
        print(f"Collection '{collection_from}' does not exist.")
        return
    
    # Ensure the target collection exists, if not, create it
    if collection_to not in bpy.data.collections:
        target_collection = bpy.data.collections.new(collection_to)
        bpy.context.scene.collection.children.link(target_collection)
    else:
        target_collection = bpy.data.collections[collection_to]
    
    # Get the collection to delete
    collection_to_delete = bpy.data.collections[collection_from]
    
    # Move all objects to the target collection
    for obj in collection_to_delete.objects:
        target_collection.objects.link(obj)
    
    # Unlink the objects from the collection to delete
    for obj in collection_to_delete.objects:
        collection_to_delete.objects.unlink(obj)
    
    # Delete the collection
    bpy.data.collections.remove(collection_to_delete)

    return target_collection



def save_collection_backup(context, collection):

    bpy.ops.wm.save_mainfile()

    # Get the current blend file path
    blend_filepath = bpy.data.filepath
    if not blend_filepath:
        print("Save the .blend file first.")
        return
    
    # Get the directory of the current blend file
    directory = os.path.dirname(blend_filepath)

    
    if not os.path.exists(directory + "\Backups"):
        os.makedirs(directory + "\Backups")


    backup_filepath = create_unique_path(collection, directory)
        

    new_collection_name = 'Backup - ' + collection.name

    new_collection = move_objects_from_collection(collection.name, new_collection_name)

    # Deselect all collections
    for coll in bpy.data.collections:
        coll.hide_viewport = True

    # Select only the target collection
    new_collection.hide_viewport = False
    
    # Remove all collections except the selected one
    for coll in bpy.data.collections:
        if coll != new_collection:
            bpy.data.collections.remove(coll)
    
    # Create a new blend file for the backup
    bpy.ops.wm.save_as_mainfile(filepath=backup_filepath, copy=True)
    
    # Reopen the original blend file
    bpy.ops.wm.open_mainfile(filepath=blend_filepath)

# Operator for saving collection backup
class OBJECT_OT_save_collection_backup(bpy.types.Operator):
    bl_idname = "object.save_collection_backup"
    bl_label = "Save Backup"
    
    collection_name: bpy.props.StringProperty()
    
    def execute(self, context):
        if bpy.data.is_saved:
            collection = bpy.data.collections.get(self.collection_name)
            if collection:
                save_collection_backup(context, collection)
                self.report({'INFO'}, f"Backup saved.")
            else:
                self.report({'ERROR'}, f"Collection not found")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, f"You need to save you .blend file!")
            return {'FINISHED'}


# Menu entry for the context menu
def menu_func(self, context):
    layout = self.layout
    selected_collection = context.collection
    if selected_collection:
        layout.operator(OBJECT_OT_save_collection_backup.bl_idname, text="Save Backup").collection_name = selected_collection.name

    layout.operator(OBJECT_OT_save_selected_objects_backup.bl_idname, text="Save Backup")

# Registering the operator and menu
def register():
    bpy.utils.register_class(OBJECT_OT_save_collection_backup)
    bpy.types.OUTLINER_MT_collection.append(menu_func)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_save_collection_backup)
    bpy.types.OUTLINER_MT_collection.remove(menu_func)

if __name__ == "__main__":
    register()
