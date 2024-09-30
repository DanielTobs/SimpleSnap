# SimpleSnap Add-On for Blender

**SimpleSnap** is a Blender add-on designed to facilitate the alignment of selected objects with the ground. It provides tools to quickly snap mesh objects to specific positions, similar to vertex snapping in other software like Unreal. With customizable options for distance limits, offsets, and rotations, it streamlines your workflow in scenes.

## Features

- **Snap to Ground**: Easily move selected objects to the ground based on various criteria:
  - Adjust to the nearest mesh object's origin.
  - Snap to the bottom of selected objects.
  - Customize snap behavior with a **Gap Offset** to control the distance between objects and the surface.

- **Add Control**: Create an empty object at the lowest point of selected objects, with customizable size and Z offset. This is useful for organizing and parenting objects.
  - Specify the size of the empty for better visibility.
  - Control the Z offset to position the empty at a precise height above the ground.

- **Randomization Options**:
  - Randomly rotate the selected object around the X, Y, and Z axes before snapping.

- **Flexible Target Selection**: Choose to snap to all objects or only mesh objects.

- **Snap to Normal**: Option to align the object to the surface normal of the closest object.

- **Undo Functionality**: Restore objects to their original position and rotation after snapping or after creating an empty.

- **User-Friendly Panel**: Access all options conveniently within a dedicated panel in the 3D view.

## Installation

1. Click the green button **Code > Download Zip** to download the add-on to your computer.
2. In Blender, go to **Edit > Preferences > Add-ons**.
3. Click **Install...** in the top-right corner and select the downloaded archive.
4. Enable the add-on from the list.

## Add-On Hotkeys and Settings

- By default, activate the tool using the **End** key to snap selected objects to the ground.
- Use the **Undo Snap** button to restore the previous position and rotation.
- Use the **Add Control** button to generate an empty at the lowest point of selected objects.
- Customize settings directly from the panel, including the **Gap Offset**, empty size, and randomization options.

![screenshot](https://imgur.com/ZihNUFt.jpg)

## Using the Tool

1. Select the object(s) you want to snap to the ground.
2. Press the **End** key to execute the snap.
3. Optionally, adjust settings such as detection distance and rotation randomization in the panel before snapping.
4. To create an empty, select the desired objects and click **Add Control**.

## Important Notes

This tool is optimized for standard use; performance may decrease with very high-polygon models or many objects under the mouse. For best results, isolate or hide unnecessary objects in your scene before using the tool.

## Bug Report

If you encounter issues, please ensure you have the latest version of the add-on. If problems persist:

- Create an issue [here](https://github.com/DanielTobs/SimpleSnap/issues), or feel free to modify the code and let me know if you make any progress in that case.
- Provide a detailed description of the problem, including what you were doing and your scene setup.

## Known Issues / Limitations

- The randomization features may not function as expected in all scenarios; please report any anomalies.
- The tool is designed primarily for mesh, curve, empty objects, and armatures; results may vary with other object types.

## Version Support

Compatible with Blender 4.2 and newer.
