import bpy
import bmesh
from mathutils import Vector
import random

class SnapToGroundOperator(bpy.types.Operator):
    bl_idname = "object.snap_to_ground"
    bl_label = "Snap to Ground"
    bl_description = "Moves selected objects down to the ground."

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        selected_objects = context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "No objects selected.")
            return {'CANCELLED'}

        # Store original position and rotation for undo
        for obj in selected_objects:
            obj["original_location"] = obj.location.copy()
            obj["original_rotation"] = obj.rotation_euler.copy()

        # Retrieve scene properties
        distance_limit = context.scene.snap_detection_distance_limit
        offset_x = context.scene.snap_offset_x
        offset_y = context.scene.snap_offset_y
        random_offset_x = context.scene.snap_random_offset_x
        random_offset_y = context.scene.snap_random_offset_y
        rotate_randomly_x = context.scene.snap_randomize_rotation_x
        rotate_randomly_y = context.scene.snap_randomize_rotation_y
        rotate_randomly_z = context.scene.snap_randomize_rotation_z
        object_type = context.scene.snap_object_type
        rotate_to_normal = context.scene.snap_rotate_to_normal

        for obj in selected_objects:
            if obj.type != 'MESH':
                continue  # Only process mesh objects

            # Apply random rotation first
            if rotate_randomly_x:
                obj.rotation_euler.x += random.uniform(-180, 180) * (3.14159 / 180)  # Convert degrees to radians

            if rotate_randomly_y:
                obj.rotation_euler.y += random.uniform(-180, 180) * (3.14159 / 180)  # Convert degrees to radians

            if rotate_randomly_z:
                obj.rotation_euler.z += random.uniform(-180, 180) * (3.14159 / 180)  # Convert degrees to radians

            original_location = obj.location.copy()
            closest_obj = None
            closest_distance = float('inf')
            obj_bottom_z = original_location.z - (obj.dimensions.z / 2)

            for other in context.scene.objects:
                if other != obj and (object_type == 'ALL' or other.type == 'MESH'):
                    other_bottom_z = other.location.z - (other.dimensions.z / 2)
                    distance = obj_bottom_z - other_bottom_z

                    if distance > 0 and abs(distance) < distance_limit:
                        if (abs(original_location.x - other.location.x) < (obj.dimensions.x / 2 + other.dimensions.x / 2) and
                            abs(original_location.y - other.location.y) < (obj.dimensions.y / 2 + other.dimensions.y / 2)):
                            
                            if abs(distance) < closest_distance:
                                closest_distance = abs(distance)
                                closest_obj = other

            if closest_obj:
                # Adjust position
                obj.location.z = closest_obj.location.z + (closest_obj.dimensions.z / 2 + obj.dimensions.z / 2)
                
                # Apply random offset in X and Y
                obj.location.x += offset_x + random.uniform(-random_offset_x, random_offset_x)
                obj.location.y += offset_y + random.uniform(-random_offset_y, random_offset_y)

                if rotate_to_normal:
                    # Calculate surface normal
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

                self.report({'INFO'}, f"Snapped {obj.name} to ground with offsets ({offset_x}, {offset_y})")
            else:
                self.report({'WARNING'}, f"No closest object found below for {obj.name}.")

        return {'FINISHED'}

class UndoSnapOperator(bpy.types.Operator):
    bl_idname = "object.undo_snap_to_ground"
    bl_label = "Undo Snap to Ground"
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
                del obj["original_location"]  # Remove property after use
                del obj["original_rotation"]  # Remove property after use
                self.report({'INFO'}, f"Restored position and rotation of {obj.name}")
            else:
                self.report({'WARNING'}, f"No original position found for {obj.name}.")
        
        return {'FINISHED'}

class SnapPanel(bpy.types.Panel):
    bl_label = "Snap to Ground"
    bl_idname = "OBJECT_PT_snap_to_ground"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Snap'

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def draw(self, context):
        layout = self.layout
        layout.label(text="Press 'End' to snap")

        snap_operator = layout.operator(SnapToGroundOperator.bl_idname, text="Snap to Ground")
        undo_operator = layout.operator(UndoSnapOperator.bl_idname, text="Undo Snap")
        
        # Panel properties
        layout.prop(context.scene, "snap_detection_distance_limit")
        layout.prop(context.scene, "snap_offset_x")
        layout.prop(context.scene, "snap_offset_y")
        layout.prop(context.scene, "snap_random_offset_x")
        layout.prop(context.scene, "snap_random_offset_y")
        layout.prop(context.scene, "snap_randomize_rotation_x")
        layout.prop(context.scene, "snap_randomize_rotation_y")
        layout.prop(context.scene, "snap_randomize_rotation_z")
        layout.prop(context.scene, "snap_object_type")
        layout.prop(context.scene, "snap_rotate_to_normal")

def register():
    bpy.utils.register_class(SnapToGroundOperator)
    bpy.utils.register_class(UndoSnapOperator)
    bpy.utils.register_class(SnapPanel)

    # Register properties in the scene context
    bpy.types.Scene.snap_detection_distance_limit = bpy.props.FloatProperty(
        name="Detection Distance Limit",
        default=100.0,
        min=0.0,
        max=100000.0,
        step=0.1
    )
    bpy.types.Scene.snap_offset_x = bpy.props.FloatProperty(
        name="Offset X",
        default=0.0,
        min=-10.0,
        max=10.0,
        step=0.1
    )
    bpy.types.Scene.snap_offset_y = bpy.props.FloatProperty(
        name="Offset Y",
        default=0.0,
        min=-10.0,
        max=10.0,
        step=0.1
    )
    bpy.types.Scene.snap_random_offset_x = bpy.props.FloatProperty(
        name="Random Offset X",
        default=0.0,
        min=0.0,
        max=10.0,
        step=0.1
    )
    bpy.types.Scene.snap_random_offset_y = bpy.props.FloatProperty(
        name="Random Offset Y",
        default=0.0,
        min=0.0,
        max=10.0,
        step=0.1
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

def unregister():
    bpy.utils.unregister_class(SnapPanel)
    bpy.utils.unregister_class(SnapToGroundOperator)
    bpy.utils.unregister_class(UndoSnapOperator)

    # Unregister properties
    del bpy.types.Scene.snap_detection_distance_limit
    del bpy.types.Scene.snap_offset_x
    del bpy.types.Scene.snap_offset_y
    del bpy.types.Scene.snap_random_offset_x
    del bpy.types.Scene.snap_random_offset_y
    del bpy.types.Scene.snap_randomize_rotation_x
    del bpy.types.Scene.snap_randomize_rotation_y
    del bpy.types.Scene.snap_randomize_rotation_z
    del bpy.types.Scene.snap_object_type
    del bpy.types.Scene.snap_rotate_to_normal

if __name__ == "__main__":
    register()
