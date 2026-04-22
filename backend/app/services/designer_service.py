"""
Designer service to orchestrate 2D floor plan rendering.
Supports matplotlib preview, professional DXF export (NanoCAD compatible), and MCP hooks.
"""
from __future__ import annotations
import logging
import os
from typing import Optional

from app.models.schemas import BuildingSpec
from app.blender.floor_plan_renderer import render_floor_plan as matplotlib_render
from app.services.cad_exporter import export_to_dxf

logger = logging.getLogger(__name__)

class DesignerService:
    def __init__(self):
        # Hooks for MCP or external API keys can be initialized here
        self.mcp_enabled = os.getenv("MCP_DESIGNER_ENABLED", "false").lower() == "true"

    def render_all(self, spec: BuildingSpec, output_dir: str) -> dict:
        """
        Produce both a quick preview (PNG) and a professional CAD file (DXF).
        """
        results = {}

        # 1. Quick Preview (Matplotlib)
        try:
            preview_path = matplotlib_render(spec, output_dir)
            results["preview_png"] = preview_path
        except Exception as e:
            logger.error("Matplotlib preview failed: %s", e)

        # 2. Professional CAD Export (ezdxf - NanoCAD compatible)
        try:
            dxf_path = export_to_dxf(spec, output_dir)
            results["cad_dxf"] = dxf_path
        except Exception as e:
            logger.error("DXF export failed: %s", e)

        # 3. Optional MCP Hook
        if self.mcp_enabled:
            mcp_result = self.invoke_mcp_designer(spec)
            if mcp_result:
                results["mcp_output"] = mcp_result

        return results

    def invoke_mcp_designer(self, spec: BuildingSpec) -> Optional[str]:
        """
        Hook for invoking an MCP-based designer tool if available.
        This would use the Model Context Protocol to talk to a remote CAD instance.
        """
        logger.info("Attempting to invoke MCP designer...")
        # Implementation depends on the specific MCP server tool name
        # For now, this is a placeholder for future integration
        return None
