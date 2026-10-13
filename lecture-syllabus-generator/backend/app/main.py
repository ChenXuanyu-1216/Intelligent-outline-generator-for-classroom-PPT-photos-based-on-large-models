from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from app.config import settings, FRONTEND_DIR
from app.db import init_db
from app.errors import AppError, app_error_handler, generic_error_handler
from app.routers import meta, tasks, outline, export

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, generic_error_handler)

app.include_router(meta.router)
app.include_router(tasks.router)
app.include_router(outline.router)
app.include_router(export.router)


@app.on_event("startup")
def startup():
    init_db()


if FRONTEND_DIR.exists():
    app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
    app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")

    @app.get("/")
    async def index():
        return FileResponse(FRONTEND_DIR / "index.html")

    @app.get("/{page}.html")
    async def frontend_page(page: str):
        file_path = FRONTEND_DIR / f"{page}.html"
        if file_path.exists():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIR / "index.html")