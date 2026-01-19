from __future__ import annotations

from pathlib import Path
from typing import cast

from fastapi import APIRouter, Request
from fastapi.responses import Response

from engine.catalog.loader import ControlSummary, load_catalog_controls
from engine.catalog.manifest import CatalogManifest, load_manifest
from engine.catalog.paths import get_catalog_data_dir, get_manifest_path
from web.routes.wizard_steps import build_wizard_steps

router = APIRouter()


@router.get("/controls", response_class=Response)
def control_picker(request: Request) -> Response:
    templates = request.app.state.templates
    data_dir = get_catalog_data_dir()
    manifest_path = get_manifest_path()
    manifest: CatalogManifest | None = None
    controls: list[ControlSummary] = []
    active_catalog: Path | None = None

    if manifest_path.exists():
        manifest = load_manifest(str(manifest_path))
        catalog_entry = next(
            (item for item in manifest.items if item.kind == "catalog"), None
        )
        if catalog_entry:
            active_catalog = data_dir / catalog_entry.filename
            controls = load_catalog_controls(active_catalog)

    response = templates.TemplateResponse(
        request,
        "wizard/control_picker.html",
        {
            "manifest": manifest,
            "controls": controls,
            "active_catalog": active_catalog.name if active_catalog else None,
            "current_nav": "control-picker",
            "wizard_steps": build_wizard_steps(4)[0],
            "wizard_current": build_wizard_steps(4)[1],
            "breadcrumbs": [
                {"label": "Home", "href": "/"},
                {"label": "Control Picker", "href": None},
            ],
        },
    )
    return cast(Response, response)
