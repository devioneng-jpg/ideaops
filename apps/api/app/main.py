import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import health, ideas, twilio

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="IdeaOps API",
    version="0.1.0",
    description="Multi-agent idea-to-project-brief pipeline",
)

# CORS — allow Next.js dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router)
app.include_router(ideas.router)
app.include_router(twilio.router)
