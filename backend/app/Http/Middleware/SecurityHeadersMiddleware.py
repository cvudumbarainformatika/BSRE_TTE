from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Menyediakan proteksi Helmet-style HTTP Headers untuk keamanan microservice rekam medis
    """
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        
        # Helmet-style security headers (mengizinkan embed PDF viewer lintas port/origin SIMRS & Portal TTE)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self' http: https: data: blob:; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob: http: https:; "
            "font-src 'self' data:; "
            "frame-src 'self' http: https: data: blob:; "
            "frame-ancestors *; "
            "connect-src 'self' http: https: ws: wss:;"
        )
        return response
