"""Deployment security defaults; configure trusted front-end origins explicitly."""
import os
from fastapi import Request
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

class ResponseHardeningMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        max_bytes=1_048_576
        length=request.headers.get("content-length")
        if length:
            try:
                if int(length)>max_bytes:
                    return JSONResponse({"detail":"Request body too large"},status_code=413)
            except ValueError:
                return JSONResponse({"detail":"Invalid content length"},status_code=400)
        response=await call_next(request)
        response.headers["X-Content-Type-Options"]="nosniff"
        response.headers["Referrer-Policy"]="no-referrer"
        response.headers["X-Frame-Options"]="DENY"
        response.headers["Cache-Control"]="no-store" if request.url.path.startswith("/v1/private") else "no-cache"
        response.headers["Permissions-Policy"]="camera=(), microphone=(), geolocation=()"
        if os.getenv("JUMUISHA_HTTPS_ONLY")=="true":
            response.headers["Strict-Transport-Security"]="max-age=63072000; includeSubDomains"
        return response

def install_security(app):
    app.add_middleware(ResponseHardeningMiddleware)
    origins=[x.strip() for x in os.getenv("JUMUISHA_ALLOWED_ORIGINS","").split(",") if x.strip()]
    if origins:
        app.add_middleware(CORSMiddleware, allow_origins=origins,allow_methods=["GET","POST","DELETE"],allow_headers=["Authorization","Content-Type"],allow_credentials=False)
