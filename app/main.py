from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.routes_auth import router as auth_router
from app.api.routes_files import router as files_router
from app.api.routes_health import router as health_router
load_dotenv()

#Content addressible storage vault project
def create_app() -> FastAPI:
    app = FastAPI(title="CAS Vault")
    app.include_router(auth_router)
    app.include_router(files_router)
    app.include_router(health_router)
    app.mount('/', StaticFiles(directory='app/web', html=True), name='web')
    return app
