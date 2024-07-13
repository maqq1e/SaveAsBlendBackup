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

def save_collection_backup(context, collection):

    bpy.ops.wm.save_mainfile()

    # Get the current blend file path
    blend_filepath = bpy.data.filepath
    if not blend_filepath:
        print("Save the .blend file first.")
        return
    
    # Get the directory of the current blend file
    directory = os.path.dirname(blend_filepath)
    
    # Set the filename for the backup
    backup_filename = f"{collection.name}.blend"
    backup_filepath = os.path.join(directory, backup_filename)
    
    # Deselect all collections
    for coll in bpy.data.collections:
        coll.hide_viewport = True

    # Select only the target collection
    collection.hide_viewport = False
    
    # Remove all collections except the selected one
    for coll in bpy.data.collections:
        if coll != collection:
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

# Registering the operator and menu
def register():
    bpy.utils.register_class(OBJECT_OT_save_collection_backup)
    bpy.types.OUTLINER_MT_collection.append(menu_func)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_save_collection_backup)
    bpy.types.OUTLINER_MT_collection.remove(menu_func)

if __name__ == "__main__":
    register()
