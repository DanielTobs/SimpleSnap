bl_info = {
    "name": "Snap to Ground",
    "blender": (2, 82, 0),
    "category": "3D View",
}

from . import snap_to_ground

def register():
    snap_to_ground.register()

def unregister():
    snap_to_ground.unregister()