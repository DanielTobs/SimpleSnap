bl_info = {
    "name": "SimpleSnap",
    "blender": (4, 2, 0),
    "category": "Object",
    "description": "Snap selected mesh objects to the ground with customizable settings.",
    "author": "Tobs",
    "version": (1, 0),
}

import bpy
from .simple_snap import *

def register():
    # Registra las clases del addon
    bpy.utils.register_class(SnapToGroundOperator)
    bpy.utils.register_class(UndoSnapOperator)
    bpy.utils.register_class(SnapPanel)
    bpy.utils.register_class(SimpleSnapKeymap)

    # Registra las propiedades en el contexto de la escena
    bpy.types.Scene.snap_detection_distance_limit = bpy.props.FloatProperty(
        name="Detection Distance Limit",
        default=100.0,
        min=0.0,
        max=100000.0,
        step=0.1
    )
    bpy.types.Scene.snap_gap_offset = bpy.props.FloatProperty(
        name="Gap Offset",
        default=0.01,  # Valor predeterminado para Gap Offset
        min=-10.0,
        max=10.0,
        step=0.01
    )
    bpy.types.Scene.snap_randomize_rotation_x = bpy.props.BoolProperty(name="Randomize Rotation X", default=False)
    bpy.types.Scene.snap_randomize_rotation_y = bpy.props.BoolProperty(name="Randomize Rotation Y", default=False)
    bpy.types.Scene.snap_randomize_rotation_z = bpy.props.BoolProperty(name="Randomize Rotation Z", default=False)
    bpy.types.Scene.snap_object_type = bpy.props.EnumProperty(
        name="Object Type",
        items=[
            ('MESH', "MESH", "Only consider mesh objects"),
            ('ALL', "ALL", "Consider all objects")
        ],
        default='MESH'
    )
    bpy.types.Scene.snap_rotate_to_normal = bpy.props.BoolProperty(name="Rotate to Normal", default=False)

    # Agrega el keymap
    wm = bpy.context.window_manager
    km = wm.keyconfigs.default.keymaps['3D View']
    kmi = km.keymap_items.new(SimpleSnapKeymap.bl_idname, 'END', 'PRESS')

def unregister():
    # Desregistra las clases del addon
    bpy.utils.unregister_class(SnapPanel)
    bpy.utils.unregister_class(SnapToGroundOperator)
    bpy.utils.unregister_class(UndoSnapOperator)
    bpy.utils.unregister_class(SimpleSnapKeymap)

    # Desregistra las propiedades
    del bpy.types.Scene.snap_detection_distance_limit
    del bpy.types.Scene.snap_gap_offset
    del bpy.types.Scene.snap_randomize_rotation_x
    del bpy.types.Scene.snap_randomize_rotation_y
    del bpy.types.Scene.snap_randomize_rotation_z
    del bpy.types.Scene.snap_object_type
    del bpy.types.Scene.snap_rotate_to_normal

    # Elimina el keymap
    wm = bpy.context.window_manager
    km = wm.keyconfigs.default.keymaps['3D View']
    for kmi in km.keymap_items:
        if kmi.idname == SimpleSnapKeymap.bl_idname:
            km.keymap_items.remove(kmi)
            break

if __name__ == "__main__":
    register()