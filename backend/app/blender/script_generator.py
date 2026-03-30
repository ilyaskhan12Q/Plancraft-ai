"""
Blender Python script generator.
Converts a BuildingSpec into a self-contained Blender Python script
that builds the 3D scene and renders PNG + exports GLB + STL.
"""
from __future__ import annotations
import json
import os
import textwrap
from typing import List

from app.blender.materials import get_material, hex_to_rgb
from app.models.schemas import BuildingSpec, FloorSpec, RoomSpec


def _mat_block(name: str, params: dict) -> str:
    """Generate Blender Python code to create a Principled BSDF material."""
    bc = params.get("base_color", (0.8, 0.8, 0.8, 1.0))
    rough = params.get("roughness", 0.8)
    metal = params.get("metallic", 0.0)
    spec = params.get("specular", 0.5)
    trans = params.get("transmission", 0.0)
    ior = params.get("ior", 1.5)

    return textwrap.dedent(f"""\
    mat_{name} = bpy.data.materials.new(name="{name}")
    mat_{name}.use_nodes = True
    _bsdf_{name} = mat_{name}.node_tree.nodes["Principled BSDF"]
    _bsdf_{name}.inputs["Base Color"].default_value = {tuple(bc)}
    _bsdf_{name}.inputs["Roughness"].default_value = {rough}
    _bsdf_{name}.inputs["Metallic"].default_value = {metal}
    _bsdf_{name}.inputs["Specular IOR Level"].default_value = {spec}
    _bsdf_{name}.inputs["Transmission Weight"].default_value = {trans}
    _bsdf_{name}.inputs["IOR"].default_value = {ior}
    """)


def generate_blender_script(spec: BuildingSpec, output_dir: str) -> str:
    """
    Generate a Blender Python script string for the given BuildingSpec.
    output_dir: directory where the rendered files will be saved.
    """
    render_png = os.path.join(output_dir, "render.png").replace("\\", "/")
    model_glb = os.path.join(output_dir, "model.glb").replace("\\", "/")
    model_stl = os.path.join(output_dir, "model.stl").replace("\\", "/")

    wall_color = hex_to_rgb(spec.exterior_color)
    roof_color = hex_to_rgb(spec.roof_color)
    wall_params = {**get_material(spec.facade_material), "base_color": wall_color}
    roof_params = {**get_material("roof_flat"), "base_color": roof_color}
    glass_params = get_material("glass")
    door_params = get_material("door_wood")
    ground_params = get_material("grass")

    # Camera
    cam = spec.camera
    cam_pos = list(cam.pos)
    cam_target = list(cam.look_at)

    # Collect floor/wall geometry
    wall_lines: List[str] = []
    floor_base = 0.0

    for fl in spec.floors:
        fh = fl.height
        for rm in fl.rooms:
            x, y, w, d = rm.x, rm.y, rm.width, rm.depth
            z = floor_base
            # Create walls as thin boxes for each side
            wall_lines.append(
                f"# Floor {fl.floor_number} — {rm.name}\n"
                f"add_wall({x}, {y}, {z}, {w}, 0.2, {fh})  # south wall\n"
                f"add_wall({x}, {y + d - 0.2}, {z}, {w}, 0.2, {fh})  # north wall\n"
                f"add_wall({x}, {y}, {z}, 0.2, {d}, {fh})  # west wall\n"
                f"add_wall({x + w - 0.2}, {y}, {z}, 0.2, {d}, {fh})  # east wall\n"
                f"add_slab({x}, {y}, {z}, {w}, {d}, 0.2)  # floor slab\n"
            )
            if rm.has_window:
                wx = x + w / 2
                wy = y + d
                wz = z + fh * 0.55
                wall_lines.append(
                    f"add_window({wx}, {wy + 0.1}, {wz}, 1.2, 0.1, 1.0)\n"
                )
        floor_base += fh

    # Roof geometry
    total_height = sum(fl.height for fl in spec.floors)
    if spec.floors:
        first_fl = spec.floors[0]
        all_rooms = [rm for fl in spec.floors for rm in fl.rooms]
        if all_rooms:
            xs = [rm.x for rm in all_rooms] + [rm.x + rm.width for rm in all_rooms]
            ys = [rm.y for rm in all_rooms] + [rm.y + rm.depth for rm in all_rooms]
            bx, by = min(xs), min(ys)
            bw, bd = max(xs) - bx, max(ys) - by
        else:
            bx, by, bw, bd = 0, 0, 10, 8
    else:
        bx, by, bw, bd = 0, 0, 10, 8

    if spec.roof_type == "gable":
        roof_code = (
            f"add_gable_roof({bx}, {by}, {total_height}, {bw}, {bd}, 2.0)"
        )
    elif spec.roof_type == "hip":
        roof_code = (
            f"add_hip_roof({bx}, {by}, {total_height}, {bw}, {bd}, 2.0)"
        )
    else:
        # Flat roof
        roof_code = (
            f"add_slab({bx}, {by}, {total_height}, {bw}, {bd}, 0.3)"
        )

    wall_code = "".join(wall_lines)

    script = f"""\
import bpy
import math
import os

# ── Cleanup ──────────────────────────────────────────────────────────────────
bpy.ops.wm.read_factory_settings(use_empty=True)
for obj in bpy.data.objects:
    bpy.data.objects.remove(obj, do_unlink=True)

# ── Helper functions ──────────────────────────────────────────────────────────
def add_wall(x, y, z, w, d, h):
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(x + w/2, y + d/2, z + h/2)
    )
    obj = bpy.context.active_object
    obj.scale = (w, d, h)
    bpy.ops.object.transform_apply(scale=True)
    obj.data.materials.append(mat_wall)
    return obj

def add_slab(x, y, z, w, d, h):
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(x + w/2, y + d/2, z + h/2)
    )
    obj = bpy.context.active_object
    obj.scale = (w, d, h)
    bpy.ops.object.transform_apply(scale=True)
    obj.data.materials.append(mat_wall)
    return obj

def add_window(x, y, z, w, d, h):
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(x, y, z)
    )
    obj = bpy.context.active_object
    obj.scale = (w, d, h)
    bpy.ops.object.transform_apply(scale=True)
    obj.data.materials.append(mat_glass)
    return obj

def add_gable_roof(x, y, z, w, d, peak):
    verts = [
        (x,     y,     z),
        (x + w, y,     z),
        (x + w, y + d, z),
        (x,     y + d, z),
        (x + w/2, y,     z + peak),
        (x + w/2, y + d, z + peak),
    ]
    faces = [(0,1,4), (1,2,5,4), (2,3,5), (3,0,4,5)]
    mesh = bpy.data.meshes.new("GableRoof")
    obj = bpy.data.objects.new("GableRoof", mesh)
    bpy.context.collection.objects.link(obj)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj.data.materials.append(mat_roof)
    return obj

def add_hip_roof(x, y, z, w, d, peak):
    cx, cy = x + w/2, y + d/2
    verts = [
        (x,     y,     z),
        (x + w, y,     z),
        (x + w, y + d, z),
        (x,     y + d, z),
        (cx,    cy,    z + peak),
    ]
    faces = [(0,1,4), (1,2,4), (2,3,4), (3,0,4)]
    mesh = bpy.data.meshes.new("HipRoof")
    obj = bpy.data.objects.new("HipRoof", mesh)
    bpy.context.collection.objects.link(obj)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj.data.materials.append(mat_roof)
    return obj

# ── Materials ──────────────────────────────────────────────────────────────────
{_mat_block("wall", wall_params)}
{_mat_block("roof", roof_params)}
{_mat_block("glass", glass_params)}
{_mat_block("door", door_params)}
{_mat_block("ground", ground_params)}

# ── Ground plane ──────────────────────────────────────────────────────────────
bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, -0.01))
ground_obj = bpy.context.active_object
ground_obj.data.materials.append(mat_ground)

# ── Building geometry ──────────────────────────────────────────────────────────
{wall_code}
{roof_code}

# ── Camera ─────────────────────────────────────────────────────────────────────
bpy.ops.object.camera_add(location={cam_pos})
cam_obj = bpy.context.active_object
target = {cam_target}
direction = (
    target[0] - {cam_pos[0]},
    target[1] - {cam_pos[1]},
    target[2] - {cam_pos[2]},
)
import mathutils
rot = mathutils.Vector(direction).to_track_quat('-Z', 'Y').to_euler()
cam_obj.rotation_euler = rot
bpy.context.scene.camera = cam_obj
cam_obj.data.lens = {cam.lens}

# ── Sun light ──────────────────────────────────────────────────────────────────
bpy.ops.object.light_add(type='SUN', location=(10, -10, 20))
sun = bpy.context.active_object
sun.data.energy = 5.0
sun.rotation_euler = (math.radians(45), 0, math.radians(30))

bpy.ops.object.light_add(type='AREA', location=(0, 0, 15))
fill = bpy.context.active_object
fill.data.energy = 200.0
fill.data.size = 10.0

# ── World sky ──────────────────────────────────────────────────────────────────
if "World" not in bpy.data.worlds:
    world = bpy.data.worlds.new("World")
else:
    world = bpy.data.worlds["World"]
bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.53, 0.81, 0.98, 1.0)
bg.inputs["Strength"].default_value = 0.8

# ── Render settings ────────────────────────────────────────────────────────────
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.eevee.taa_render_samples = 64
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = r"{render_png}"

# ── Render ─────────────────────────────────────────────────────────────────────
bpy.ops.render.render(write_still=True)

# ── Export GLB ──────────────────────────────────────────────────────────────────
bpy.ops.export_scene.gltf(
    filepath=r"{model_glb}",
    export_format='GLB',
    use_selection=False,
)

# ── Export STL ──────────────────────────────────────────────────────────────────
try:
    bpy.ops.wm.stl_export(
        filepath=r"{model_stl}",
        export_selected_objects=False,
    )
except AttributeError:
    try:
        bpy.ops.export_mesh.stl(
            filepath=r"{model_stl}",
            use_selection=False,
        )
    except Exception as e:
        print(f"STL export not available: {{e}}")

print("AI Architect: render complete.")
"""
    return script
