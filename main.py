"""
Main FastAPI application for Commercial Real Estate Analytics API.
"""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes import router

# Create FastAPI app
app = FastAPI(
    title="Commercial Real Estate Analytics API",
    description="API for analyzing commercial real estate property performance against market benchmarks",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


# Custom exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with consistent error format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.status_code, "message": exc.detail, "type": "http_error"}},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Handle validation errors with consistent error format."""
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": 422,
                "message": "Validation error",
                "type": "validation_error",
                "details": exc.errors(),
            }
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "error": {"code": 500, "message": "Internal server error", "type": "server_error"}
        },
    )


@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "service": "Commercial Real Estate Analytics API",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "market_overview": "/api/markets/{market_id}",
            "property_performance": "/api/properties/{property_id}/market-performance",
            "market_properties": "/api/markets/{market_id}/properties",
            "health": "/api/health",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
