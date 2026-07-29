from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.config import settings
from app.api import routes_complaints, routes_ai

# Creates tables on startup if they don't exist yet. For a real deployment
# you'd use Alembic migrations instead - kept simple here per the assignment.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pharma Complaint Management System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_complaints.router)
app.include_router(routes_ai.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
