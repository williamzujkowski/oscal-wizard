from fastapi import APIRouter, Request
from fastapi.responses import Response

from engine.export import export_workspace
from engine.workspace import Workspace
from engine.ids import deterministic_id

router = APIRouter()


@router.get("/export")
def export_route(request: Request) -> Response:
    system_name = "Example System"
    system_id = deterministic_id(system_name)
    workspace = Workspace(system_name=system_name, system_id=system_id)
    payload = export_workspace(workspace)
    return Response(payload, media_type="application/json")
