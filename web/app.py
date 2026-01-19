from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from web.routes.system_foundation import router as system_foundation_router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Open OSCAL Wizard")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

templates = Jinja2Templates(directory=BASE_DIR / "templates")
app.state.templates = templates

app.include_router(system_foundation_router)
