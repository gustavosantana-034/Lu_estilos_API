from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sentry_sdk
import os
from app.api.endpoints import auth, clients, products, orders, whatsapp
from app.core.config import settings

# Initialize Sentry for error monitoring
# if settings.SENTRY_DSN:
#     sentry_sdk.init(
#         dsn=settings.SENTRY_DSN,
#         traces_sample_rate=1.0,
#     )

app = FastAPI(
    title="Lu Estilo API",
    description="API for Lu Estilo clothing company sales management",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify for production to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(clients.router, prefix="/clients", tags=["Clients"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(whatsapp.router, prefix="/whatsapp", tags=["WhatsApp Integration"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Our team has been notified."},
    )

@app.get("/", tags=["Health Check"])
def health_check():
    """Endpoint to verify the API is running"""
    return {"status": "healthy", "message": "Lu Estilo API is running"}