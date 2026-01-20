from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from engine.db import create_engine, create_sessionmaker
from web.auth import configure_oauth
from web.routes.home import router as home_router
from web.routes.export import router as export_router
from web.routes.admin import router as admin_router
from web.routes.auth import router as auth_router
from web.routes.health import router as health_router
from web.routes.users import router as users_router
from web.routes.workspaces import router as workspaces_router
from web.settings import get_settings
from web.security import load_user

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


def create_app() -> FastAPI:
    app = FastAPI()

    settings = get_settings()
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
    app.state.templates = templates
    app.state.settings = settings
    templates.env.globals["settings"] = settings

    app.state.engine = create_engine(settings)
    app.state.sessionmaker = create_sessionmaker(app.state.engine)
    app.state.oauth = configure_oauth(settings)

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        session_cookie=settings.session_cookie_name,
        same_site="lax",
        https_only=settings.session_https_only,
    )

    @app.middleware("http")
    async def attach_user(request, call_next):
        request.state.user = await load_user(request)
        return await call_next(request)

    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    app.include_router(home_router)
    app.include_router(export_router)
    app.include_router(auth_router)
    app.include_router(admin_router)
    app.include_router(workspaces_router)
    app.include_router(users_router)
    app.include_router(health_router)

    return app
