import os
import sys
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add the backend dir to sys.path for proper imports
sys.path.append(str(Path(__file__).parent.parent))

from app.models.schemas import GenerateRequest, PlotSpec, Setbacks, RoomRequirements
from app.agents.architect_agent import ArchitectAgent
from app.services.designer_service import DesignerService
from app.blender.runner import run_blender_script
from app.blender.script_generator import generate_blender_script

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_standalone_generation():
    load_dotenv()
    
    # Define a high-end 10 Marla (approx 210 sqm) request
    request = GenerateRequest(
        plot=PlotSpec(
            length=20.0,
            width=10.5,
            unit="meters",
            floors=2,
            orientation="north",
            plot_type="standard",
            setbacks=Setbacks(front=3.5, back=1.5, left=1.5, right=1.5)
        ),
        rooms=RoomRequirements(
            bedrooms=4,
            bathrooms=3,
            living_room=True,
            kitchen=True,
            dining=True,
            garage=True,
            study=True
        ),
        preferred_style="modern",
        budget="luxury",
        description="A 10 Marla contemporary villa with open-plan living and large windows facing the north lawn."
    )

    job_id = "server_run_" + os.urandom(4).hex()
    output_dir = Path("outputs") / job_id
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Starting generation for Job ID: {job_id}")

    # 1. Generate Spec
    architect = ArchitectAgent()
    spec = architect.generate(request)
    logger.info("Building Specification generated.")

    # 2. Render 2D Floor Plans
    designer = DesignerService()
    design_results = designer.render_all(spec, str(output_dir / "2d"))
    logger.info(f"2D Plans generated: {design_results.get('previews')}")

    # 3. Generate Blender Script
    script = generate_blender_script(spec, str(output_dir / "3d"))
    (output_dir / "scene.py").write_text(script)
    logger.info("Blender script generated.")

    # 4. Run Blender
    logger.info("Running Blender (this may take a moment)...")
    blender_result = run_blender_script(script, str(output_dir / "3d"), "modern")
    logger.info(f"3D Render complete: {blender_result.get('render_png')}")

    # Print summary
    print("\n" + "="*50)
    print(f"GENERATION COMPLETE - Job ID: {job_id}")
    print("="*50)
    print(f"2D Floor Plans: {design_results.get('previews')}")
    print(f"Professional DXF: {design_results.get('cad_dxf')}")
    print(f"3D Render: {blender_result.get('render_png')}")
    print(f"3D Model (GLB): {blender_result.get('model_glb')}")
    print("="*50)

if __name__ == "__main__":
    run_standalone_generation()
