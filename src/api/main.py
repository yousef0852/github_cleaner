"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

# Load .env from project root (works when cwd is project root or when running from src)
_project_root = Path(__file__).resolve().parent.parent.parent
load_dotenv(_project_root / ".env")

from api.routes import scan


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan: startup/shutdown (reserve for future DB or client init)."""
    yield


app = FastAPI(
    title="GitHub Cleaner API",
    description="Portfolio auditing: scan GitHub profiles, score repos, get recommendations.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(scan.router)


@app.get("/")
def root():
    """Root URL — Render/browser checks; real API lives under /scan, /health, /docs."""
    return {
        "service": "github-cleaner",
        "docs": "/docs",
        "health": "/health",
        "scan": "POST /scan",
        "scan_voiceflow": "POST /scan/voiceflow",
    }


@app.get("/health")
def health():
    """Health check for load balancers or agents."""
    return {"status": "ok"}
