from fastapi import FastAPI
from . import models
from .database import engine
from .routers import auth, triage
from fastapi.middleware.cors import CORSMiddleware

# This command creates the database tables based on your models.py
# It will not delete or modify existing tables.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Symptom Triage API")

# Configure CORS to allow your Vue.js frontend to communicate with this backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API endpoints from your router files
app.include_router(auth.router)
app.include_router(triage.router)

@app.get("/")
def read_root():
    return {"status": "Triage API is running"}
