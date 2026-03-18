import os
import socket
import platform
import logging
import time
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from pythonjsonlogger import jsonlogger


def _build_logger(name: str) -> logging.Logger:
    """Create a logger that outputs JSON when LOG_FORMAT=json (default)."""
    log = logging.getLogger(name)
    log.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    if os.getenv("LOG_FORMAT", "json").lower() == "json":
        fmt = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
            rename_fields={"asctime": "timestamp", "levelname": "level"},
        )
    else:
        fmt = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    handler.setFormatter(fmt)
    log.addHandler(handler)
    # Prevent duplicate logs from root logger
    log.propagate = False
    return log


logger = _build_logger(__name__)

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

HTTP_REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "HTTP requests currently being processed",
    ["method", "endpoint"],
)

DEVOPS_INFO_ENDPOINT_CALLS = Counter(
    "devops_info_endpoint_calls_total",
    "Number of calls to info service endpoints",
    ["endpoint"],
)

DEVOPS_INFO_SYSTEM_COLLECTION_SECONDS = Histogram(
    "devops_info_system_collection_seconds",
    "Time spent collecting system information",
)

# Create FastAPI application
app = FastAPI(
    title="DevOps Info Service",
    description="Service providing system and runtime information",
    version="1.0.0"
)

# Configuration
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8000))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Application start time
START_TIME = datetime.now(timezone.utc)

logger.info("Application starting", extra={"version": "1.0.0", "host": os.getenv("HOST", "0.0.0.0"), "port": int(os.getenv("PORT", 8000))})


def get_system_info():
    """Collect system information."""
    started_at = time.perf_counter()
    system_info = {
        'hostname': socket.gethostname(),
        'platform': platform.system(),
        'platform_version': platform.release(),
        'architecture': platform.machine(),
        'cpu_count': os.cpu_count() or 1,
        'python_version': platform.python_version()
    }
    DEVOPS_INFO_SYSTEM_COLLECTION_SECONDS.observe(time.perf_counter() - started_at)
    return system_info


def normalize_endpoint(path: str) -> str:
    """Keep endpoint labels low-cardinality for Prometheus."""
    if path in {"/", "/health", "/metrics"}:
        return path
    return "/other"


def get_uptime():
    """Calculate application uptime."""
    delta = datetime.now(timezone.utc) - START_TIME
    seconds = int(delta.total_seconds())
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return {
        'seconds': seconds,
        'human': f"{hours} hour{'s' if hours != 1 else ''}, {minutes} minute{'s' if minutes != 1 else ''}"
    }


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every HTTP request and response in structured JSON."""
    method = request.method
    endpoint = normalize_endpoint(request.url.path)
    started_at = time.perf_counter()

    HTTP_REQUESTS_IN_PROGRESS.labels(method=method, endpoint=endpoint).inc()
    response = None
    status_code = "500"
    try:
        response = await call_next(request)
        status_code = str(response.status_code)
        return response
    finally:
        elapsed_seconds = time.perf_counter() - started_at
        duration_ms = elapsed_seconds * 1000

        HTTP_REQUESTS_IN_PROGRESS.labels(method=method, endpoint=endpoint).dec()
        if endpoint != "/metrics":
            HTTP_REQUESTS_TOTAL.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
            ).inc()
            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=method,
                endpoint=endpoint,
            ).observe(elapsed_seconds)

        logger.info(
            "http_request",
            extra={
                "method": method,
                "path": request.url.path,
                "status_code": int(status_code),
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", ""),
                "duration_ms": round(duration_ms, 2),
            },
        )


@app.get("/")
async def index(request: Request):
    """Main endpoint - service and system information."""
    DEVOPS_INFO_ENDPOINT_CALLS.labels(endpoint="/").inc()
    uptime = get_uptime()
    system_info = get_system_info()
    
    return JSONResponse({
        "service": {
            "name": "devops-info-service",
            "version": "1.0.0",
            "description": "DevOps course info service",
            "framework": "FastAPI"
        },
        "system": system_info,
        "runtime": {
            "uptime_seconds": uptime['seconds'],
            "uptime_human": uptime['human'],
            "current_time": datetime.now(timezone.utc).isoformat() + "Z",
            "timezone": "UTC"
        },
        "request": {
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get('user-agent', 'unknown'),
            "method": request.method,
            "path": request.url.path
        },
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Service information"},
            {"path": "/health", "method": "GET", "description": "Health check"}
        ]
    })


@app.get("/health")
async def health():
    """Health check endpoint."""
    DEVOPS_INFO_ENDPOINT_CALLS.labels(endpoint="/health").inc()
    uptime = get_uptime()
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "uptime_seconds": uptime['seconds']
    })


@app.get("/metrics")
async def metrics():
    """Expose Prometheus metrics."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "Endpoint does not exist",
            "path": request.url.path
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error("unexpected_error", extra={"error": str(exc), "path": request.url.path}, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    logger.info("starting_server", extra={"host": HOST, "port": PORT})
    uvicorn.run(app, host=HOST, port=PORT, log_level="info" if DEBUG else "warning")
