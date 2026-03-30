#!/usr/bin/env python3
"""
Blender smoke test — creates a trivial scene and renders it headless.
Run from backend/ directory:
    python scripts/test_blender.py
"""
import os
import sys
import tempfile
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from app.blender.runner import run_blender_script

SIMPLE_SCRIPT = """\
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
bpy.ops.object.camera_add(location=(5, -5, 5))
cam = bpy.context.active_object
bpy.context.scene.camera = cam
bpy.ops.object.light_add(type='SUN', location=(3, 3, 6))
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 4
scene.render.resolution_x = 320
scene.render.resolution_y = 240
scene.render.filepath = r"{out}"
bpy.ops.render.render(write_still=True)
print("Blender smoke test: OK")
"""

if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmpdir:
        out_png = os.path.join(tmpdir, "render.png")
        script = SIMPLE_SCRIPT.replace("{out}", out_png)
        result = run_blender_script(script, tmpdir, "test")

        if result["success"]:
            print("✅ Blender smoke test PASSED")
            print(f"   Output: {result['render_png']}")
        else:
            print("❌ Blender smoke test FAILED")
            print(f"   Error: {result.get('error', 'unknown')}")
            sys.exit(1)
