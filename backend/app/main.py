from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.core.config import settings
from app.api.endpoints import categories, products, orders, districts, promo

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(categories.router, prefix=f"{settings.API_V1_STR}/categories", tags=["categories"])
app.include_router(products.router, prefix=f"{settings.API_V1_STR}/products", tags=["products"])
app.include_router(orders.router, prefix=f"{settings.API_V1_STR}/orders", tags=["orders"])
app.include_router(districts.router, prefix=f"{settings.API_V1_STR}/districts", tags=["districts"])
app.include_router(promo.router, prefix=f"{settings.API_V1_STR}/promo", tags=["promo"])

# Serve static files (for product images)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve web app
if os.path.exists("../frontend/webapp"):
    app.mount("/webapp", StaticFiles(directory="../frontend/webapp", html=True), name="webapp")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Seafood Store API", "version": settings.VERSION}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Serve webapp index for SPA routing
@app.get("/webapp/{full_path:path}")
async def serve_webapp(full_path: str):
    """Serve web app for SPA routing"""
    webapp_dir = "../frontend/webapp"
    if os.path.exists(webapp_dir):
        return FileResponse(f"{webapp_dir}/index.html")
    return {"error": "Web app not found"}