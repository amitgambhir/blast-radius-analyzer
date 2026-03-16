import os
import sys
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

_provider = os.environ.get("LLM_PROVIDER", "anthropic").lower()
_key_map = {
    "anthropic": ("ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY=sk-ant-..."),
    "openai": ("OPENAI_API_KEY", "OPENAI_API_KEY=sk-..."),
}
_key_var, _key_hint = _key_map.get(
    _provider, ("ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY=sk-ant-...")
)
if not os.environ.get(_key_var):
    print(
        f"WARNING: {_key_var} is not set (LLM_PROVIDER={_provider}). "
        f"Analysis endpoints will fail. Add {_key_hint} to your .env file.",
        file=sys.stderr,
    )


def _get_allowed_origins() -> list[str]:
    configured = os.environ.get("CORS_ALLOW_ORIGINS", "")
    origins = [origin.strip() for origin in configured.split(",") if origin.strip()]
    if origins:
        return origins
    return [
        "http://localhost:3001",
        "http://localhost:5173",
        "http://localhost:3000",
    ]


def _get_max_request_bytes() -> int:
    raw_limit = os.environ.get("MAX_REQUEST_BYTES", "262144")
    try:
        limit = int(raw_limit)
    except ValueError:
        limit = 262144
    return max(limit, 1024)


from routers import analyze, examples, health  # noqa: E402

app = FastAPI(
    title="Blast Radius Analyzer",
    description="Map the impact of your decisions before they map you.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def enforce_request_size_limit(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > _get_max_request_bytes():
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Request body is too large."},
                )
        except ValueError:
            pass
    return await call_next(request)


app.include_router(health.router, tags=["health"])
app.include_router(analyze.router, prefix="/api", tags=["analysis"])
app.include_router(examples.router, prefix="/api", tags=["examples"])


@app.get("/")
async def root():
    return {
        "message": "Blast Radius Analyzer API",
        "docs": "/docs",
        "health": "/health",
    }
