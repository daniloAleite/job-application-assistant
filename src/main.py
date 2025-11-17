from fastapi import FastAPI

from src.api.endpoints import application


app = FastAPI(title="Job Application Assistant API")
app.include_router(application.router, prefix="/application",
                   tags=["Application Analysis"])
