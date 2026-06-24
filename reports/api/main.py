"""FastAPI application for commodity reports."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.routes import router
import os

app = FastAPI(
    title="LatAm & Caribbean Commodity Reports",
    description="Weekly updates and monthly reports on commodity markets, legal risks, and climate impacts",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
if not os.path.exists("./static/reports"):
    os.makedirs("./static/reports")
if not os.path.exists("./static/exports"):
    os.makedirs("./static/exports")

app.mount("/static", StaticFiles(directory="./static"), name="static")

# Include routes
app.include_router(router)


@app.get("/")
def read_root():
    return {
        "message": "LatAm & Caribbean Commodity Reports API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "commodity-reports"}
