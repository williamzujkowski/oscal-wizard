from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from markdown_it import MarkdownIt

from web.routes.control_interview import router as control_interview_router
from web.routes.controls import router as controls_router
from web.routes.diff_view import router as diff_router
from web.routes.home import router as home_router
from web.routes.inventory import router as inventory_router
from web.routes.parties import router as parties_router
from web.routes.system_foundation import router as system_foundation_router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Open OSCAL Wizard")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

templates = Jinja2Templates(directory=BASE_DIR / "templates")
markdown_renderer = MarkdownIt("commonmark", {"html": False})
templates.env.filters["render_markdown"] = markdown_renderer.render
app.state.templates = templates

app.include_router(system_foundation_router)
app.include_router(controls_router)
app.include_router(control_interview_router)
app.include_router(diff_router)
app.include_router(home_router)
app.include_router(inventory_router)
app.include_router(parties_router)
