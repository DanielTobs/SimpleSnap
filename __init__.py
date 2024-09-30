bl_info = {
    "name": "SimpleSnap",
    "blender": (4, 2, 0),
    "category": "Object",
    "description": "Snap selected objects to the ground with customizable options.",
    "author": "Tobs",
    "version": (1, 0, 0),
    "support": "COMMUNITY",
    "doc_url": "https://github.com/DanielTobs/SimpleSnap",
}

import bpy
import bmesh
from mathutils import Vector
import random

class SnapToGroundOperator(bpy.types.Operator):
    bl_idname = "object.snap_to_ground"
    bl_label = "Snap"
    bl_description = "Moves the control or selected objects down to the ground."

    original_positions = {}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        selected_objects = context.selected_objects
        control_empty = next((obj for obj in selected_objects if obj.type == 'EMPTY'), None)

        # Store original positions for undo functionality
        self.original_positions = {obj.name: obj.location.copy() for obj in selected_objects}

        if context.scene.clear_mesh:
            for obj in selected_objects:
                if obj.type in {'MESH', 'CURVE', 'EMPTY', 'ARMATURE'}:
                    bpy.ops.object.select_all(action='DESELECT')
                    obj.select_set(True)
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

        if context.scene.create_control and not control_empty:
            control_empty = self.create_control(context, selected_objects)

        objects_to_snap = [control_empty] if control_empty else selected_objects
        distance_limit = context.scene.snap_detection_distance_limit
        gap_offset = context.scene.snap_gap_offset
        rotate_randomly_x = context.scene.snap_randomize_rotation_x
        rotate_randomly_y = context.scene.snap_randomize_rotation_y
        rotate_randomly_z = context.scene.snap_randomize_rotation_z
        object_type = context.scene.snap_object_type
        rotate_to_normal = context.scene.snap_rotate_to_normal

        for obj in objects_to_snap:
            if obj.type not in {'MESH', 'CURVE', 'EMPTY', 'ARMATURE'}:
                continue

            if rotate_randomly_x:
                obj.rotation_euler.x += random.uniform(-180, 180) * (3.14159 / 180)

            if rotate_randomly_y:
                obj.rotation_euler.y += random.uniform(-180, 180) * (3.14159 / 180)

            if rotate_randomly_z:
                obj.rotation_euler.z += random.uniform(-180, 180) * (3.14159 / 180)

            original_location = obj.location.copy()

            if context.scene.enable_floor_selection and context.scene.target_floor_object:
                closest_obj = context.scene.target_floor_object
            else:
                # Find the closest object below
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

    def create_control(self, context, selected_objects):
        mid_point = Vector((0, 0, 0))
        total_objects = len(selected_objects)

        lowest_z = float('inf')
        for obj in selected_objects:
            if obj.type in {'MESH', 'CURVE', 'EMPTY', 'ARMATURE'}:
                mid_point += obj.location
                obj_bottom_z = obj.location.z - (obj.dimensions.z / 2)
                lowest_z = min(lowest_z, obj_bottom_z)

        if total_objects > 0:
            mid_point /= total_objects

        pivot_empty = bpy.data.objects.new("Empty", None)
        context.collection.objects.link(pivot_empty)
        pivot_empty.location = mid_point
        pivot_empty.location.z = lowest_z
        pivot_empty.empty_display_size = context.scene.pivot_empty_size

        bpy.ops.object.select_all(action='DESELECT')
        pivot_empty.select_set(True)

        for obj in selected_objects:
            if obj.type in {'MESH', 'CURVE', 'EMPTY', 'ARMATURE'}:
                obj.select_set(True)

        bpy.context.view_layer.objects.active = pivot_empty
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        self.report({'INFO'}, f"Created empty at Z: {pivot_empty.location.z}")
        return pivot_empty

class UndoOperator(bpy.types.Operator):
    bl_idname = "object.undo_snap"
    bl_label = "Undo"
    bl_description = "Restores objects to their original positions and removes the empty."

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and any(obj.type in {'MESH', 'CURVE', 'EMPTY', 'ARMATURE'} for obj in context.selected_objects)

    def execute(self, context):
        selected_objects = context.selected_objects
        pivot_empty = next((obj for obj in selected_objects if obj.type == 'EMPTY'), None)

        if pivot_empty:
            for obj in selected_objects:
                if obj.name in SnapToGroundOperator.original_positions:
                    obj.location = SnapToGroundOperator.original_positions[obj.name]
                    obj.rotation_euler = obj.rotation_euler.copy()

            if pivot_empty in selected_objects:
                bpy.ops.object.select_all(action='DESELECT')
                pivot_empty.select_set(True)
                bpy.context.view_layer.objects.active = pivot_empty
                bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
                bpy.data.objects.remove(pivot_empty)

            self.report({'INFO'}, "Restored original positions and removed empty.")
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
        layout.prop(context.scene, "clear_mesh", text="Clear Mesh (Apply Transforms & Set Origin)")
        
        layout.operator(SnapToGroundOperator.bl_idname, text="Snap")
        layout.operator(UndoOperator.bl_idname, text="Undo")

        layout.prop(context.scene, "enable_floor_selection", text="Enable Floor Selection")
        if context.scene.enable_floor_selection:
            layout.prop(context.scene, "target_floor_object", text="Target Floor Object")
        
        layout.prop(context.scene, "snap_detection_distance_limit")
        layout.prop(context.scene, "snap_gap_offset")
        layout.prop(context.scene, "snap_randomize_rotation_x")
        layout.prop(context.scene, "snap_randomize_rotation_y")
        layout.prop(context.scene, "snap_randomize_rotation_z")
        layout.prop(context.scene, "snap_object_type")
        layout.prop(context.scene, "snap_rotate_to_normal")
        
        layout.separator()

        layout.label(text="Control Options")
        layout.prop(context.scene, "create_control", text="Add Control")
        
        layout.prop(context.scene, "pivot_empty_size")
        layout.prop(context.scene, "pivot_empty_z_offset")

class SimpleSnapKeymap(bpy.types.Operator):
    bl_idname = "object.simple_snap_keymap"
    bl_label = "Simple Snap Keymap"
    bl_description = "Activates Snap to Ground with the End key."

    def modal(self, context, event):
        if event.type == 'END' and event.value == 'PRESS':
            bpy.ops.object.snap_to_ground()
            return {'RUNNING_MODAL'}
        elif event.type in {'ESC'}:
            return {'CANCELLED'}
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

def register():
    bpy.utils.register_class(SnapPanel)
    bpy.utils.register_class(SnapToGroundOperator)
    bpy.utils.register_class(UndoOperator)
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
    
    bpy.types.Scene.clear_mesh = bpy.props.BoolProperty(name="Clear Mesh", default=False, description="Apply all transforms and set origin to geometry when snapping.")
    bpy.types.Scene.create_control = bpy.props.BoolProperty(name="Add Control", default=False, description="Create a control empty when snapping.")

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

    bpy.types.Scene.enable_floor_selection = bpy.props.BoolProperty(
        name="Enable Floor Selection",
        default=False,
        description="Enable selection of the target floor object."
    )
    
    bpy.types.Scene.target_floor_object = bpy.props.PointerProperty(
        name="Target Floor Object",
        type=bpy.types.Object,
        description="Select the object to snap to."
    )

    wm = bpy.context.window_manager
    km = wm.keyconfigs.default.keymaps['3D View']
    kmi = km.keymap_items.new(SimpleSnapKeymap.bl_idname, 'END', 'PRESS')

def unregister():
    bpy.utils.unregister_class(SnapPanel)
    bpy.utils.unregister_class(SnapToGroundOperator)
    bpy.utils.unregister_class(UndoOperator)
    bpy.utils.unregister_class(SimpleSnapKeymap)

    del bpy.types.Scene.snap_detection_distance_limit
    del bpy.types.Scene.snap_gap_offset
    del bpy.types.Scene.snap_randomize_rotation_x
    del bpy.types.Scene.snap_randomize_rotation_y
    del bpy.types.Scene.snap_randomize_rotation_z
    del bpy.types.Scene.snap_object_type
    del bpy.types.Scene.snap_rotate_to_normal
    del bpy.types.Scene.clear_mesh
    del bpy.types.Scene.create_control
    del bpy.types.Scene.pivot_empty_size
    del bpy.types.Scene.pivot_empty_z_offset
    del bpy.types.Scene.enable_floor_selection
    del bpy.types.Scene.target_floor_object

    wm = bpy.context.window_manager
    km = wm.keyconfigs.default.keymaps['3D View']
    for kmi in km.keymap_items:
        if kmi.idname == SimpleSnapKeymap.bl_idname:
            km.keymap_items.remove(kmi)
            break

if __name__ == "__main__":
    register()
