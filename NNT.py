bl_info = {
    "name": "Normal Thief for Blender",
    "author": "Adapted by 3AMt from Noors",
    "version": (1, 6),
    "blender": (4, 4, 0),
    "location": "View3D > Sidebar > NNT Tab",
    "description": "Transfers normals from a source object to a target object using barycentric projection.",
    "category": "Object",
}

import bpy
from bpy.props import PointerProperty
from mathutils import Vector, kdtree, geometry


def get_closest_point_normal(point, source_obj, kd, tris, normals):
    _, index, _ = kd.find(point)
    tri = tris[index]
    tri_normals = normals[index]
    projected = geometry.closest_point_on_tri(point, *tri)
    interpolated = get_barycentric_normal(tri, tri_normals, projected)
    return interpolated


def get_barycentric_normal(tri_coords, tri_normals, point):
    bary_coords = geometry.barycentric_transform(
        point,
        tri_coords[0], tri_coords[1], tri_coords[2],
        Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
    )
    return (
        tri_normals[0] * bary_coords.x +
        tri_normals[1] * bary_coords.y +
        tri_normals[2] * bary_coords.z
    ).normalized()


def build_kdtree(source_obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = source_obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()
    mesh.calc_loop_triangles()

    kd = kdtree.KDTree(len(mesh.loop_triangles))
    tris = []
    norms = []

    for tri in mesh.loop_triangles:
        verts = [mesh.vertices[i].co.copy() for i in tri.vertices]
        norms_ = [mesh.loops[i].normal.copy() for i in tri.loops]
        center = sum(verts, Vector()) / 3.0
        kd.insert(center, len(tris))
        tris.append(verts)
        norms.append(norms_)

    kd.balance()
    return kd, tris, norms


def transfer_normals(source, target):
    if not isinstance(target.data, bpy.types.Mesh):
        raise TypeError("Target must be a mesh object.")

    mesh = target.data
    if hasattr(mesh, 'use_auto_smooth'):
        mesh.use_auto_smooth = True

    mesh.calc_loop_triangles()
    kd, tris, normals = build_kdtree(source)

    custom_normals = [None] * len(mesh.loops)

    for tri in mesh.loop_triangles:
        for li in tri.loops:
            loop = mesh.loops[li]
            vertex = mesh.vertices[loop.vertex_index]
            world_pos = target.matrix_world @ vertex.co
            interpolated = get_closest_point_normal(world_pos, source, kd, tris, normals)
            custom_normals[li] = interpolated @ target.matrix_world.inverted_safe().transposed()

    for i, n in enumerate(custom_normals):
        if n is None:
            custom_normals[i] = mesh.loops[i].normal

    mesh.normals_split_custom_set(custom_normals)
    mesh.update()


class NNTProps(bpy.types.PropertyGroup):
    source_obj: PointerProperty(type=bpy.types.Object, name="Source")
    target_obj: PointerProperty(type=bpy.types.Object, name="Target")


class OBJECT_OT_transfer_normals(bpy.types.Operator):
    bl_idname = "object.nnt_transfer_normals"
    bl_label = "Transfer Normals"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.nnt_props
        source = props.source_obj
        target = props.target_obj

        if not source or not target or source == target:
            self.report({'ERROR'}, "Source and target must be different mesh objects.")
            return {'CANCELLED'}

        try:
            transfer_normals(source, target)
            self.report({'INFO'}, "Normals transferred.")
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        return {'FINISHED'}


class VIEW3D_PT_nnt_panel(bpy.types.Panel):
    bl_label = "3AM Tree Normal Thief"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "NNT"

    def draw(self, context):
        layout = self.layout
        props = context.scene.nnt_props

        layout.prop(props, "source_obj")
        layout.prop(props, "target_obj")
        layout.operator("object.nnt_transfer_normals")


classes = [
    NNTProps,
    OBJECT_OT_transfer_normals,
    VIEW3D_PT_nnt_panel,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.nnt_props = bpy.props.PointerProperty(type=NNTProps)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.nnt_props

if __name__ == "__main__":
    register()
