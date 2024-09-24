# SimpleSnap Add-On for Blender

SimpleSnap is a Blender add-on designed to quickly snap selected mesh objects to the ground, similar to vertex snapping in other 3D software like Maya and 3ds Max. With customizable settings for distance limits, offsets, and rotation, it streamlines the process of aligning objects in your scene.

## Features

- **Snap to Ground**: Easily move selected objects to the ground based on various criteria:
  - Snap to the nearest mesh object's origin.
  - Snap to the bottom of selected objects.
  - Customize snap behavior with a **Gap Offset** to control the distance between objects and the surface.

- **Randomization Options**:
  - Randomly rotate the selected object around the X, Y, and Z axes before snapping.

- **Flexible Target Selection**: Choose to snap to all objects or only mesh objects.

- **Snap to Normal**: Option to align the object to the surface normal of the closest object.

- **Undo Functionality**: Restore objects to their original position and rotation after snapping.

- **User-Friendly Panel**: Access all options conveniently within a dedicated panel in the 3D view.

## Installation

1. Click on the green button **Code > Download Zip** to download the add-on to your computer.
2. In Blender, go to **Edit > Preferences > Add-ons**.
3. Click **Install...** in the top-right corner and select the downloaded archive.
4. Enable the add-on from the list.

## Add-On Hotkeys and Settings

- By default, enable the tool using the **End** key to snap selected objects to the ground.
- Use the **Undo Snap** button to restore the previous position and rotation.
- Customize settings directly from the panel, including the **Gap Offset** and randomization options.

  ![screenshot](https://imgur.com/IBRfcFB.jpg)

## Using the Tool

1. Select the object(s) you want to snap to the ground.
2. Press the **End** key to execute the snap.
3. Optionally, adjust settings such as detection distance and rotation randomization in the panel before snapping.

## Important Notes

  This tool is optimized for standard use; performance may decrease with very high-polygon models or many objects under the mouse.
  For best results, isolate or hide unnecessary objects in your scene before using the tool.

## Bug Report

If you encounter issues, please ensure you have the latest version of the add-on. If problems persist:

 - Create an issue here, or feel free to modify the code, let me know if you make any progress in that case. https://github.com/DanielTobs/SimpleSnap/issues
 - Provide a detailed description of the problem, including what you were doing and your scene setup.

## Known Issues / Limitations

 - The randomization features may not function as expected in all scenarios; please report any anomalies.
 - The tool is designed primarily for mesh objects; results may vary with other object types.

## Version Support

Compatible with Blender 4.2 and newer.
