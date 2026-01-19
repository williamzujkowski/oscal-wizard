from __future__ import annotations

from typing import cast

from fastapi import APIRouter, Request
from fastapi.responses import Response

from engine.catalog.manifest import CatalogManifest, load_manifest
from engine.catalog.paths import get_manifest_path

router = APIRouter()


@router.get("/settings", response_class=Response)
def settings(request: Request) -> Response:
    templates = request.app.state.templates
    manifest_path = get_manifest_path()
    manifest: CatalogManifest | None = None
    if manifest_path.exists():
        manifest = load_manifest(str(manifest_path))

    response = templates.TemplateResponse(
        request,
        "wizard/settings.html",
        {
            "manifest": manifest,
            "current_nav": "settings",
            "breadcrumbs": [
                {"label": "Home", "href": "/"},
                {"label": "Settings", "href": None},
            ],
        },
    )
    return cast(Response, response)
