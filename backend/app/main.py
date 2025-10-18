"""FastAPI Application Main Entry Point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.api.routes import auth

# Import routes (we'll add more as we create them)
# from app.api.routes import movies, ratings, reviews, recommendations, users, watchlist

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Movie Recommendation System with Neural Collaborative Filtering",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - Allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
# app.include_router(movies.router, prefix="/api/movies", tags=["Movies"])
# app.include_router(ratings.router, prefix="/api/ratings", tags=["Ratings"])
# app.include_router(reviews.router, prefix="/api/reviews", tags=["Reviews"])
# app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
# app.include_router(users.router, prefix="/api/users", tags=["Users"])
# app.include_router(watchlist.router, prefix="/api/watchlist", tags=["Watchlist"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print(f"[STARTUP] {settings.APP_NAME} v{settings.APP_VERSION} started!")
    print(f"[DOCS] Documentation: http://localhost:8000/docs")
    print(f"[ENV] Environment: {settings.ENVIRONMENT}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
