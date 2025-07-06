from fastapi import FastAPI
from . import models, database, routes
from .auth_doc import router as auth_router

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Inventory API")

origins = [
    'http://localhost:5173',
]

app.add_middleware(
    "fastapi.middleware.cors.CORSMiddleware",
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router)
app.include_router(auth_router)
