from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
import os

app = FastAPI(
    title="Trade Finance Optimizer",
    description="Multi-agent system for identifying optimal trade finance (LC) opportunities in LatAm",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.get("/")
def read_root():
    return {
        "message": "Trade Finance Optimizer API",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "trade-finance-optimizer"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=True
    )
