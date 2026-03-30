"""
Blender headless runner.
"""
from __future__ import annotations
import logging
import os
import subprocess
import tempfile
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

BLENDER_PATH = os.getenv("BLENDER_PATH", "/usr/bin/blender")
RENDER_TIMEOUT = int(os.getenv("BLENDER_TIMEOUT", "900"))  # 15 min max


def run_blender_script(
    script_content: str,
    output_dir: str,
    variant: str = "modern",
    timeout: int = RENDER_TIMEOUT,
) -> dict:
    """
    Write the script to a temp file and run Blender headless.
    Returns {"success": bool, "render_png": str, "model_glb": str, "model_stl": str}
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", prefix=f"ai_arch_{variant}_", delete=False
    ) as f:
        f.write(script_content)
        script_path = f.name

    logger.info("Running Blender headless: %s | script: %s", BLENDER_PATH, script_path)

    try:
        result = subprocess.run(
            [
                BLENDER_PATH,
                "--background",
                "--python", script_path,
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            logger.error("Blender stderr:\n%s", result.stderr[-3000:])
            return {"success": False, "error": result.stderr[-500:]}

        render_png = os.path.join(output_dir, "render.png")
        model_glb = os.path.join(output_dir, "model.glb")
        model_stl = os.path.join(output_dir, "model.stl")

        success = os.path.exists(render_png)
        logger.info("Blender render success=%s | output_dir=%s", success, output_dir)

        return {
            "success": success,
            "render_png": render_png if os.path.exists(render_png) else None,
            "model_glb": model_glb if os.path.exists(model_glb) else None,
            "model_stl": model_stl if os.path.exists(model_stl) else None,
        }
    except subprocess.TimeoutExpired:
        logger.error("Blender timed out after %ds", timeout)
        return {"success": False, "error": "Blender render timed out"}
    except FileNotFoundError:
        logger.error("Blender not found at: %s", BLENDER_PATH)
        return {"success": False, "error": f"Blender not found at {BLENDER_PATH}"}
    finally:
        try:
            os.unlink(script_path)
        except OSError:
            pass
