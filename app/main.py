from fastapi import FastAPI
from . import models, database, routes
from .auth_doc import router as auth_router

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Inventory API")

app.include_router(routes.router)
app.include_router(auth_router)
