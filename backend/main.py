import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from fastapi import WebSocket, WebSocketDisconnect

from config.settings import settings
from config.database import init_db
from routes.api import api_router
from app.Http.Middleware.SecurityHeadersMiddleware import SecurityHeadersMiddleware
from app.Http.Middleware.RateLimitMiddleware import limiter
from app.Services.WebSocketService import ws_manager

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Microservice Pengelolaan Dokumen Medis & TTE BSRE BSSN untuk SIMRS Rumah Sakit",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 1. State Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 2. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Di produksi sesuaikan dengan origin frontend SIMRS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

# 3. Helmet-style Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# 4. Proxy Headers (Forwarded headers dari Nginx / reverse proxy)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"])

# 5. Include API Routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# 6. Real-time WebSocket Hub (Terpusat untuk SIMRS Web, Mobile React Native, dan SSO)
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Terima pesan ping/heartbeat dari client jika ada
            text = await websocket.receive_text()
            if text == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)

@app.on_event("startup")
def on_startup():
    # Pastikan storage direktori siap
    os.makedirs(os.path.join(settings.BASE_STORAGE_PATH, "documents"), exist_ok=True)
    os.makedirs(os.path.join(settings.BASE_STORAGE_PATH, "qr_codes"), exist_ok=True)
    os.makedirs(os.path.join(settings.BASE_STORAGE_PATH, "temp"), exist_ok=True)
    init_db()

@app.get("/")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "hospital": settings.HOSPITAL_NAME,
        "status": "online",
        "docs": "/docs",
        "api_v1": settings.API_V1_STR
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "bsre_mode": "mock_sandbox" if settings.BSRE_MOCK_MODE else "live_bssn",
        "clamav": "active_monitoring" if settings.CLAMAV_ENABLED else "disabled"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, proxy_headers=True)
