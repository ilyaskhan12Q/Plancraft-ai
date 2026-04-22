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
mat_wall = bpy.data.materials.new(name="wall")
mat_wall.use_nodes = True
_bsdf_wall = mat_wall.node_tree.nodes["Principled BSDF"]
_bsdf_wall.inputs["Base Color"].default_value = (0.7454042095403874, 0.7454042095403874, 0.7454042095403874, 1.0)
_bsdf_wall.inputs["Roughness"].default_value = 0.88
_bsdf_wall.inputs["Metallic"].default_value = 0.0
_bsdf_wall.inputs["Specular IOR Level"].default_value = 0.05
_bsdf_wall.inputs["Transmission Weight"].default_value = 0.0
_bsdf_wall.inputs["IOR"].default_value = 1.5

mat_roof = bpy.data.materials.new(name="roof")
mat_roof.use_nodes = True
_bsdf_roof = mat_roof.node_tree.nodes["Principled BSDF"]
_bsdf_roof.inputs["Base Color"].default_value = (0.033104766570885055, 0.033104766570885055, 0.033104766570885055, 1.0)
_bsdf_roof.inputs["Roughness"].default_value = 0.9
_bsdf_roof.inputs["Metallic"].default_value = 0.0
_bsdf_roof.inputs["Specular IOR Level"].default_value = 0.02
_bsdf_roof.inputs["Transmission Weight"].default_value = 0.0
_bsdf_roof.inputs["IOR"].default_value = 1.5

mat_glass = bpy.data.materials.new(name="glass")
mat_glass.use_nodes = True
_bsdf_glass = mat_glass.node_tree.nodes["Principled BSDF"]
_bsdf_glass.inputs["Base Color"].default_value = (0.7, 0.85, 0.95, 0.1)
_bsdf_glass.inputs["Roughness"].default_value = 0.0
_bsdf_glass.inputs["Metallic"].default_value = 0.0
_bsdf_glass.inputs["Specular IOR Level"].default_value = 1.0
_bsdf_glass.inputs["Transmission Weight"].default_value = 0.95
_bsdf_glass.inputs["IOR"].default_value = 1.45

mat_door = bpy.data.materials.new(name="door")
mat_door.use_nodes = True
_bsdf_door = mat_door.node_tree.nodes["Principled BSDF"]
_bsdf_door.inputs["Base Color"].default_value = (0.4, 0.25, 0.1, 1.0)
_bsdf_door.inputs["Roughness"].default_value = 0.6
_bsdf_door.inputs["Metallic"].default_value = 0.0
_bsdf_door.inputs["Specular IOR Level"].default_value = 0.15
_bsdf_door.inputs["Transmission Weight"].default_value = 0.0
_bsdf_door.inputs["IOR"].default_value = 1.5

mat_ground = bpy.data.materials.new(name="ground")
mat_ground.use_nodes = True
_bsdf_ground = mat_ground.node_tree.nodes["Principled BSDF"]
_bsdf_ground.inputs["Base Color"].default_value = (0.18, 0.38, 0.12, 1.0)
_bsdf_ground.inputs["Roughness"].default_value = 0.95
_bsdf_ground.inputs["Metallic"].default_value = 0.0
_bsdf_ground.inputs["Specular IOR Level"].default_value = 0.0
_bsdf_ground.inputs["Transmission Weight"].default_value = 0.0
_bsdf_ground.inputs["IOR"].default_value = 1.5


# ── Ground plane ──────────────────────────────────────────────────────────────
bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, -0.01))
ground_obj = bpy.context.active_object
ground_obj.data.materials.append(mat_ground)

# ── Building geometry ──────────────────────────────────────────────────────────
# Floor 0 — Garage
add_wall(0.0, 0.0, 0.0, 3.0, 0.2, 3.5)  # south wall
add_wall(0.0, 5.8, 0.0, 3.0, 0.2, 3.5)  # north wall
add_wall(0.0, 0.0, 0.0, 0.2, 6.0, 3.5)  # west wall
add_wall(2.8, 0.0, 0.0, 0.2, 6.0, 3.5)  # east wall
add_slab(0.0, 0.0, 0.0, 3.0, 6.0, 0.2)  # floor slab
# Floor 0 — Entrance Foyer
add_wall(3.0, 0.0, 0.0, 2.5, 0.2, 3.5)  # south wall
add_wall(3.0, 2.8, 0.0, 2.5, 0.2, 3.5)  # north wall
add_wall(3.0, 0.0, 0.0, 0.2, 3.0, 3.5)  # west wall
add_wall(5.3, 0.0, 0.0, 0.2, 3.0, 3.5)  # east wall
add_slab(3.0, 0.0, 0.0, 2.5, 3.0, 0.2)  # floor slab
add_window(4.25, 3.1, 1.9250000000000003, 1.2, 0.1, 1.0)
# Floor 0 — Powder Room
add_wall(5.5, 0.0, 0.0, 2.0, 0.2, 3.5)  # south wall
add_wall(5.5, 1.8, 0.0, 2.0, 0.2, 3.5)  # north wall
add_wall(5.5, 0.0, 0.0, 0.2, 2.0, 3.5)  # west wall
add_wall(7.3, 0.0, 0.0, 0.2, 2.0, 3.5)  # east wall
add_slab(5.5, 0.0, 0.0, 2.0, 2.0, 0.2)  # floor slab
# Floor 0 — G.F. Hallway
add_wall(3.0, 3.0, 0.0, 4.5, 0.2, 3.5)  # south wall
add_wall(3.0, 5.8, 0.0, 4.5, 0.2, 3.5)  # north wall
add_wall(3.0, 3.0, 0.0, 0.2, 3.0, 3.5)  # west wall
add_wall(7.3, 3.0, 0.0, 0.2, 3.0, 3.5)  # east wall
add_slab(3.0, 3.0, 0.0, 4.5, 3.0, 0.2)  # floor slab
# Floor 0 — Stairs G.F.
add_wall(6.0, 3.0, 0.0, 1.5, 0.2, 3.5)  # south wall
add_wall(6.0, 5.8, 0.0, 1.5, 0.2, 3.5)  # north wall
add_wall(6.0, 3.0, 0.0, 0.2, 3.0, 3.5)  # west wall
add_wall(7.3, 3.0, 0.0, 0.2, 3.0, 3.5)  # east wall
add_slab(6.0, 3.0, 0.0, 1.5, 3.0, 0.2)  # floor slab
# Floor 0 — Living Room
add_wall(0.0, 6.0, 0.0, 7.5, 0.2, 3.5)  # south wall
add_wall(0.0, 10.8, 0.0, 7.5, 0.2, 3.5)  # north wall
add_wall(0.0, 6.0, 0.0, 0.2, 5.0, 3.5)  # west wall
add_wall(7.3, 6.0, 0.0, 0.2, 5.0, 3.5)  # east wall
add_slab(0.0, 6.0, 0.0, 7.5, 5.0, 0.2)  # floor slab
add_window(3.75, 11.1, 1.9250000000000003, 1.2, 0.1, 1.0)
# Floor 0 — Dining Area
add_wall(0.0, 11.0, 0.0, 4.0, 0.2, 3.5)  # south wall
add_wall(0.0, 13.8, 0.0, 4.0, 0.2, 3.5)  # north wall
add_wall(0.0, 11.0, 0.0, 0.2, 3.0, 3.5)  # west wall
add_wall(3.8, 11.0, 0.0, 0.2, 3.0, 3.5)  # east wall
add_slab(0.0, 11.0, 0.0, 4.0, 3.0, 0.2)  # floor slab
add_window(2.0, 14.1, 1.9250000000000003, 1.2, 0.1, 1.0)
# Floor 0 — Kitchen
add_wall(4.0, 11.0, 0.0, 3.5, 0.2, 3.5)  # south wall
add_wall(4.0, 13.8, 0.0, 3.5, 0.2, 3.5)  # north wall
add_wall(4.0, 11.0, 0.0, 0.2, 3.0, 3.5)  # west wall
add_wall(7.3, 11.0, 0.0, 0.2, 3.0, 3.5)  # east wall
add_slab(4.0, 11.0, 0.0, 3.5, 3.0, 0.2)  # floor slab
add_window(5.75, 14.1, 1.9250000000000003, 1.2, 0.1, 1.0)
# Floor 0 — Scullery/Laundry
add_wall(4.0, 14.0, 0.0, 3.5, 0.2, 3.5)  # south wall
add_wall(4.0, 15.8, 0.0, 3.5, 0.2, 3.5)  # north wall
add_wall(4.0, 14.0, 0.0, 0.2, 2.0, 3.5)  # west wall
add_wall(7.3, 14.0, 0.0, 0.2, 2.0, 3.5)  # east wall
add_slab(4.0, 14.0, 0.0, 3.5, 2.0, 0.2)  # floor slab
add_window(5.75, 16.1, 1.9250000000000003, 1.2, 0.1, 1.0)
# Floor 1 — Upper Hallway
add_wall(0.0, 0.0, 3.5, 7.5, 0.2, 3.2)  # south wall
add_wall(0.0, 3.8, 3.5, 7.5, 0.2, 3.2)  # north wall
add_wall(0.0, 0.0, 3.5, 0.2, 4.0, 3.2)  # west wall
add_wall(7.3, 0.0, 3.5, 0.2, 4.0, 3.2)  # east wall
add_slab(0.0, 0.0, 3.5, 7.5, 4.0, 0.2)  # floor slab
add_window(3.75, 4.1, 5.26, 1.2, 0.1, 1.0)
# Floor 1 — Master Bedroom
add_wall(0.0, 10.0, 3.5, 4.0, 0.2, 3.2)  # south wall
add_wall(0.0, 14.8, 3.5, 4.0, 0.2, 3.2)  # north wall
add_wall(0.0, 10.0, 3.5, 0.2, 5.0, 3.2)  # west wall
add_wall(3.8, 10.0, 3.5, 0.2, 5.0, 3.2)  # east wall
add_slab(0.0, 10.0, 3.5, 4.0, 5.0, 0.2)  # floor slab
add_window(2.0, 15.1, 5.26, 1.2, 0.1, 1.0)
# Floor 1 — Master Bathroom
add_wall(0.0, 7.5, 3.5, 2.5, 0.2, 3.2)  # south wall
add_wall(0.0, 9.8, 3.5, 2.5, 0.2, 3.2)  # north wall
add_wall(0.0, 7.5, 3.5, 0.2, 2.5, 3.2)  # west wall
add_wall(2.3, 7.5, 3.5, 0.2, 2.5, 3.2)  # east wall
add_slab(0.0, 7.5, 3.5, 2.5, 2.5, 0.2)  # floor slab
add_window(1.25, 10.1, 5.26, 1.2, 0.1, 1.0)
# Floor 1 — Walk-in Closet
add_wall(2.5, 7.5, 3.5, 1.5, 0.2, 3.2)  # south wall
add_wall(2.5, 9.8, 3.5, 1.5, 0.2, 3.2)  # north wall
add_wall(2.5, 7.5, 3.5, 0.2, 2.5, 3.2)  # west wall
add_wall(3.8, 7.5, 3.5, 0.2, 2.5, 3.2)  # east wall
add_slab(2.5, 7.5, 3.5, 1.5, 2.5, 0.2)  # floor slab
# Floor 1 — Bedroom 2
add_wall(4.0, 10.0, 3.5, 3.5, 0.2, 3.2)  # south wall
add_wall(4.0, 14.8, 3.5, 3.5, 0.2, 3.2)  # north wall
add_wall(4.0, 10.0, 3.5, 0.2, 5.0, 3.2)  # west wall
add_wall(7.3, 10.0, 3.5, 0.2, 5.0, 3.2)  # east wall
add_slab(4.0, 10.0, 3.5, 3.5, 5.0, 0.2)  # floor slab
add_window(5.75, 15.1, 5.26, 1.2, 0.1, 1.0)
# Floor 1 — Bathroom 2
add_wall(5.5, 7.5, 3.5, 2.0, 0.2, 3.2)  # south wall
add_wall(5.5, 9.8, 3.5, 2.0, 0.2, 3.2)  # north wall
add_wall(5.5, 7.5, 3.5, 0.2, 2.5, 3.2)  # west wall
add_wall(7.3, 7.5, 3.5, 0.2, 2.5, 3.2)  # east wall
add_slab(5.5, 7.5, 3.5, 2.0, 2.5, 0.2)  # floor slab
add_window(6.5, 10.1, 5.26, 1.2, 0.1, 1.0)
# Floor 1 — Bedroom 3
add_wall(0.0, 3.0, 3.5, 3.5, 0.2, 3.2)  # south wall
add_wall(0.0, 6.8, 3.5, 3.5, 0.2, 3.2)  # north wall
add_wall(0.0, 3.0, 3.5, 0.2, 4.0, 3.2)  # west wall
add_wall(3.3, 3.0, 3.5, 0.2, 4.0, 3.2)  # east wall
add_slab(0.0, 3.0, 3.5, 3.5, 4.0, 0.2)  # floor slab
add_window(1.75, 7.1, 5.26, 1.2, 0.1, 1.0)
# Floor 1 — Bathroom 3
add_wall(0.0, 7.0, 3.5, 2.0, 0.2, 3.2)  # south wall
add_wall(0.0, 9.3, 3.5, 2.0, 0.2, 3.2)  # north wall
add_wall(0.0, 7.0, 3.5, 0.2, 2.5, 3.2)  # west wall
add_wall(1.8, 7.0, 3.5, 0.2, 2.5, 3.2)  # east wall
add_slab(0.0, 7.0, 3.5, 2.0, 2.5, 0.2)  # floor slab
add_window(1.0, 9.6, 5.26, 1.2, 0.1, 1.0)
# Floor 1 — Home Theatre/Study
add_wall(4.0, 3.0, 3.5, 3.5, 0.2, 3.2)  # south wall
add_wall(4.0, 6.8, 3.5, 3.5, 0.2, 3.2)  # north wall
add_wall(4.0, 3.0, 3.5, 0.2, 4.0, 3.2)  # west wall
add_wall(7.3, 3.0, 3.5, 0.2, 4.0, 3.2)  # east wall
add_slab(4.0, 3.0, 3.5, 3.5, 4.0, 0.2)  # floor slab

add_slab(0.0, 0.0, 6.7, 7.5, 16.0, 0.3)

# ── Camera ─────────────────────────────────────────────────────────────────────
bpy.ops.object.camera_add(location=[10.0, -10.0, 15.0])
cam_obj = bpy.context.active_object
target = [3.75, 7.5, 3.0]
direction = (
    target[0] - 10.0,
    target[1] - -10.0,
    target[2] - 15.0,
)
import mathutils
rot = mathutils.Vector(direction).to_track_quat('-Z', 'Y').to_euler()
cam_obj.rotation_euler = rot
bpy.context.scene.camera = cam_obj
cam_obj.data.lens = 35.0

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
scene.render.filepath = r"outputs/server_run_0dcd7815/3d/render.png"

# ── Render ─────────────────────────────────────────────────────────────────────
bpy.ops.render.render(write_still=True)

# ── Export GLB ──────────────────────────────────────────────────────────────────
bpy.ops.export_scene.gltf(
    filepath=r"outputs/server_run_0dcd7815/3d/model.glb",
    export_format='GLB',
    use_selection=False,
)

# ── Export STL ──────────────────────────────────────────────────────────────────
try:
    bpy.ops.wm.stl_export(
        filepath=r"outputs/server_run_0dcd7815/3d/model.stl",
        export_selected_objects=False,
    )
except AttributeError:
    try:
        bpy.ops.export_mesh.stl(
            filepath=r"outputs/server_run_0dcd7815/3d/model.stl",
            use_selection=False,
        )
    except Exception as e:
        print(f"STL export not available: {e}")

print("AI Architect: render complete.")
