🌲 3AM Tree Normal Thief for Blender

Normal Thief is a Blender addon designed to generate realistic shading normals for tree and foliage assets by transferring smoothed normals from a reference object—typically a half-sphere "dome" - to the target tree mesh. This technique greatly enhances how lighting interacts with foliage, creating a more natural and cohesive look in real-time engines or renders.

✅ Why Use It?

Tree assets often suffer from harsh or unrealistic shading due to their complex geometry. This addon solves that by projecting soft, clean normals from a simplified shape (like a dome) onto the tree mesh, emulating the effect of spherical normals without destroying the mesh topology.

This is especially useful for:

    Game assets needing smooth shading for tree canopies.

    Baking lighting or normal maps with improved realism.

    Optimizing stylized foliage in low-poly or mid-poly environments.

How to Use

    Create a reference dome:

        Add a UV sphere large enough to fully cover the tree.

        Delete the bottom half, leaving a hemisphere that sits above your tree (like a dome).

    Install and enable the addon in Blender.

    In the NNT Tab (View3D Sidebar):

        Set the half-sphere as the Source.

        Set the tree mesh as the Target.

    Click “Transfer Normals”.

That’s it. Your tree now has beautifully blended normals.

How It Works (Tech Summary)

    Builds a KD-tree of triangle centers from the source object.

    For each loop in the target mesh, finds the closest triangle in the source.

    Uses barycentric interpolation to compute smooth normals.

    Applies the custom normals non-destructively using Blender's normals_split_custom_set.

Credits

Originally created by Noors, adapted and enhanced by 3AMt for foliage asset workflows.
