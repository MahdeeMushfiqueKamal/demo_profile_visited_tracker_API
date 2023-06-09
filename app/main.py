from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .constants import TITLE, VERSION
from .routers import profile_visit, status


def start_application(title, version):
    application = FastAPI(title=title, version=version)
    application.include_router(status.router)
    application.include_router(profile_visit.router)
    return application


app = start_application(title=TITLE, version=VERSION)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)
