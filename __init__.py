bl_info = {
    "name": "SimpleSnap",
    "blender": (4, 2, 0),
    "category": "Object",
    "description": "Snap selected mesh objects to the ground with customizable settings.",
    "author": "Tobs",
    "version": (1, 0),
}

import bpy
import bmesh
from mathutils import Vector
import random

class SnapToGroundOperator(bpy.types.Operator):
    bl_idname = "object.snap_to_ground"
    bl_label = "Snap"
    bl_description = "Moves selected objects down to the ground."

    @classmethod
    def poll(cls, context):
        return context.selected_objects
    
    def execute(self, context):
        selected_objects = context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "No objects selected.")
            return {'CANCELLED'}

        for obj in selected_objects:
            obj["original_location"] = obj.location.copy()
            obj["original_rotation"] = obj.rotation_euler.copy()

        distance_limit = context.scene.snap_detection_distance_limit
        gap_offset = context.scene.snap_gap_offset
        rotate_randomly_x = context.scene.snap_randomize_rotation_x
        rotate_randomly_y = context.scene.snap_randomize_rotation_y
        rotate_randomly_z = context.scene.snap_randomize_rotation_z
        object_type = context.scene.snap_object_type
        rotate_to_normal = context.scene.snap_rotate_to_normal

        for obj in selected_objects:
            if obj.type not in {'MESH', 'CURVE', 'EMPTY', 'ARMATURE'}:
                continue

            if rotate_randomly_x:
                obj.rotation_euler.x += random.uniform(-180, 180) * (3.14159 / 180)

            if rotate_randomly_y:
                obj.rotation_euler.y += random.uniform(-180, 180) * (3.14159 / 180)

            if rotate_randomly_z:
                obj.rotation_euler.z += random.uniform(-180, 180) * (3.14159 / 180)

            original_location = obj.location.copy()
            closest_obj = None
            closest_distance = float('inf')
            obj_bottom_z = original_location.z - (obj.dimensions.z / 2)

            for other in context.scene.objects:
                if other != obj and (object_type == 'ALL' or other.type in {'MESH', 'CURVE', 'EMPTY', 'ARMATURE'}):
                    other_bottom_z = other.location.z - (other.dimensions.z / 2)
                    distance = obj_bottom_z - other_bottom_z

                    if distance > 0 and abs(distance) < distance_limit:
                        if (abs(original_location.x - other.location.x) < (obj.dimensions.x / 2 + other.dimensions.x / 2) and
                            abs(original_location.y - other.location.y) < (obj.dimensions.y / 2 + other.dimensions.y / 2)):
                            
                            if abs(distance) < closest_distance:
                                closest_distance = abs(distance)
                                closest_obj = other

            if closest_obj:
                obj.location.z = closest_obj.location.z + (closest_obj.dimensions.z / 2 + obj.dimensions.z / 2 + gap_offset)

                if rotate_to_normal and obj.type == 'MESH':
                    bm = bmesh.new()
                    bm.from_mesh(closest_obj.data)
                    face_normal = None

                    for face in bm.faces:
                        if face.select:
                            face_normal = face.normal
                            break

                    if face_normal is not None:
                        rot = face_normal.to_track_quat('Z', 'Y')
                        obj.rotation_euler = rot.to_euler()

                    bm.free()

                self.report({'INFO'}, f"Snapped {obj.name} to ground with Gap Offset {gap_offset}")
            else:
                self.report({'WARNING'}, f"No closest object found below for {obj.name}.")

        return {'FINISHED'}

class UndoSnapOperator(bpy.types.Operator):
    bl_idname = "object.undo_snap_to_ground"
    bl_label = "Undo Snap"
    bl_description = "Restores selected objects to their original position and rotation."

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        selected_objects = context.selected_objects
        for obj in selected_objects:
            if "original_location" in obj and "original_rotation" in obj:
                obj.location = obj["original_location"]
                obj.rotation_euler = obj["original_rotation"]
                del obj["original_location"]
                del obj["original_rotation"]
                self.report({'INFO'}, f"Restored position and rotation of {obj.name}")
            else:
                self.report({'WARNING'}, f"No original position found for {obj.name}.")
        
        return {'FINISHED'}

class CreatePivotOperator(bpy.types.Operator):
    bl_idname = "object.create_empty"
    bl_label = "Add Control"
    bl_description = "Creates an empty at the lowest position of selected objects and parents them with Keep Transform."

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        selected_objects = context.selected_objects
        
        if not selected_objects:
            self.report({'WARNING'}, "No objects selected.")
            return {'CANCELLED'}

        custom_size = context.scene.pivot_empty_size
        z_offset = context.scene.pivot_empty_z_offset

        mid_point = Vector((0, 0, 0))
        total_objects = len(selected_objects)

        lowest_z = float('inf')
        for obj in selected_objects:
            if obj.type in {'MESH', 'CURVE', 'EMPTY', 'ARMATURE'}:
                mid_point += obj.location

                if obj.type == 'ARMATURE':
                    for bone in obj.data.bones:
                        if bone.use_deform:
                            bone_bottom_z = obj.location.z + bone.head.z - (bone.length / 2)
                            lowest_z = min(lowest_z, bone_bottom_z)
                else:
                    obj_bottom_z = obj.location.z - (obj.dimensions.z / 2)
                    lowest_z = min(lowest_z, obj_bottom_z)

        if total_objects > 0:
            mid_point /= total_objects

        pivot_empty = bpy.data.objects.new("Empty", None)
        context.collection.objects.link(pivot_empty)
        pivot_empty.location = mid_point

        pivot_empty.location.z = lowest_z + z_offset
        pivot_empty.empty_display_size = custom_size

        bpy.ops.object.select_all(action='DESELECT')
        pivot_empty.select_set(True)

        for obj in selected_objects:
            if obj.type in {'MESH', 'CURVE', 'EMPTY', 'ARMATURE'}:
                obj.select_set(True)

        bpy.context.view_layer.objects.active = pivot_empty
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        self.report({'INFO'}, f"Created empty at Z: {pivot_empty.location.z}")
        return {'FINISHED'}

class UndoCreatePivotOperator(bpy.types.Operator):
    bl_idname = "object.undo_create_empty"
    bl_label = "Undo Add Control"
    bl_description = "Restores objects to their original parent and removes the empty."

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        selected_objects = context.selected_objects
        pivot_empty = next((obj for obj in context.collection.objects if obj.name == "Empty"), None)

        if pivot_empty:
            for obj in selected_objects:
                if obj.parent == pivot_empty:
                    obj.parent = None
                    obj.location = obj.matrix_world.to_translation()
                    obj.rotation_euler = obj.rotation_euler.copy()

            bpy.ops.object.select_all(action='DESELECT')
            pivot_empty.select_set(True)
            bpy.context.view_layer.objects.active = pivot_empty
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
            bpy.data.objects.remove(pivot_empty)

            self.report({'INFO'}, "Restored original parent and removed empty.")
        else:
            self.report({'WARNING'}, "No empty found.")

        return {'FINISHED'}

class SnapPanel(bpy.types.Panel):
    bl_label = "SimpleSnap"
    bl_idname = "OBJECT_PT_simple_snap"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Snap'

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def draw(self, context):
        layout = self.layout
        
        layout.label(text="Snap Options")
        layout.operator(SnapToGroundOperator.bl_idname, text="Snap")
        layout.operator(UndoSnapOperator.bl_idname, text="Undo Snap")
        
        layout.label(text="Press 'END' to snap quickly.")
        
        layout.prop(context.scene, "snap_detection_distance_limit")
        layout.prop(context.scene, "snap_gap_offset")
        layout.prop(context.scene, "snap_randomize_rotation_x")
        layout.prop(context.scene, "snap_randomize_rotation_y")
        layout.prop(context.scene, "snap_randomize_rotation_z")
        layout.prop(context.scene, "snap_object_type")
        layout.prop(context.scene, "snap_rotate_to_normal")

        layout.separator()

        layout.label(text="Control Options")
        layout.operator(CreatePivotOperator.bl_idname, text="Add Control")
        layout.operator(UndoCreatePivotOperator.bl_idname, text="Undo Add Control")
        
        layout.prop(context.scene, "pivot_empty_size")
        layout.prop(context.scene, "pivot_empty_z_offset")

class SimpleSnapKeymap(bpy.types.KeyMapItem):
    bl_idname = "simple_snap_keymap"
    bl_label = "Simple Snap Keymap"

    def modal(self, context, event):
        if event.type == 'END' and event.value == 'PRESS':
            bpy.ops.object.snap_to_ground()
            return {'FINISHED'}
        return {'PASS_THROUGH'}

def register():
    bpy.utils.register_class(SnapToGroundOperator)
    bpy.utils.register_class(UndoSnapOperator)
    bpy.utils.register_class(CreatePivotOperator)
    bpy.utils.register_class(UndoCreatePivotOperator)
    bpy.utils.register_class(SnapPanel)
    bpy.utils.register_class(SimpleSnapKeymap)

    bpy.types.Scene.snap_detection_distance_limit = bpy.props.FloatProperty(
        name="Detection Distance Limit",
        default=100.0,
        min=0.0,
        max=100000.0,
        step=0.1
    )
    bpy.types.Scene.snap_gap_offset = bpy.props.FloatProperty(
        name="Gap Offset",
        default=0.01,
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

    bpy.types.Scene.pivot_empty_size = bpy.props.FloatProperty(
        name="Control Size",
        default=1.0,
        min=0.0,
        step=0.1
    )
    bpy.types.Scene.pivot_empty_z_offset = bpy.props.FloatProperty(
        name="Control Z Offset",
        default=0.0,
        min=-10.0,
        max=10.0,
        step=0.1
    )

    wm = bpy.context.window_manager
    km = wm.keyconfigs.default.keymaps['3D View']
    kmi = km.keymap_items.new(SimpleSnapKeymap.bl_idname, 'END', 'PRESS')

def unregister():
    bpy.utils.unregister_class(SnapPanel)
    bpy.utils.unregister_class(SnapToGroundOperator)
    bpy.utils.unregister_class(UndoSnapOperator)
    bpy.utils.unregister_class(CreatePivotOperator)
    bpy.utils.unregister_class(UndoCreatePivotOperator)
    bpy.utils.unregister_class(SimpleSnapKeymap)

    del bpy.types.Scene.snap_detection_distance_limit
    del bpy.types.Scene.snap_gap_offset
    del bpy.types.Scene.snap_randomize_rotation_x
    del bpy.types.Scene.snap_randomize_rotation_y
    del bpy.types.Scene.snap_randomize_rotation_z
    del bpy.types.Scene.snap_object_type
    del bpy.types.Scene.snap_rotate_to_normal
    del bpy.types.Scene.pivot_empty_size
    del bpy.types.Scene.pivot_empty_z_offset

    wm = bpy.context.window_manager
    km = wm.keyconfigs.default.keymaps['3D View']
    for kmi in km.keymap_items:
        if kmi.idname == SimpleSnapKeymap.bl_idname:
            km.keymap_items.remove(kmi)
            break

if __name__ == "__main__":
    register()
