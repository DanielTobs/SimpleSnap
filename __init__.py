bl_info = {
    "name": "SimpleSnap",
    "blender": (4, 2, 0),
    "category": "Object",
}

import bpy
from .simple_snap import register, unregister

def register():
    register()

def unregister():
    unregister()

if __name__ == "__main__":
    register()