import asyncio
import subprocess
import time
from datetime import datetime, timezone

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Ollama Generate API", version="1.0.0")


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="The text prompt to send to the model")
    model: str = Field(default="gpt-oss:20b", description="Ollama model name to use")


class GenerateResponse(BaseModel):
    output: str = Field(..., description="Generated text from the model")
    model: str = Field(..., description="Model that was used")
    start_time_human: str = Field(..., description="Request start time in human-readable ISO format")
    start_time_unix: float = Field(..., description="Request start time as Unix timestamp")
    duration_ms: float = Field(..., description="Duration of the generation in milliseconds")
    duration_human: str = Field(..., description="Duration as HH:MM:SS.sss (HH/MM omitted if 0)")


def _format_duration_ms(ms: float) -> str:
    """Format milliseconds as HH:MM:SS.sss, omitting HH if 0 and MM if 0."""
    total_secs = ms / 1000.0
    h = int(total_secs // 3600)
    m = int((total_secs % 3600) // 60)
    s = total_secs % 60
    if h > 0:
        return f"{h}:{m:02d}:{s:06.3f}"
    if m > 0:
        return f"{m}:{s:06.3f}"
    return f"{s:.3f}"


def _run_ollama(model: str, prompt: str) -> subprocess.CompletedProcess:
    """Blocking ollama run; intended to be called from a thread."""
    return subprocess.run(
        ["ollama", "run", model, prompt],
        capture_output=True,
        text=True,
        timeout=300,
    )


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest) -> GenerateResponse:
    """Generate text using Ollama with the given prompt. Handles concurrent requests without blocking."""
    start_time_unix = time.time()
    start_time_human = datetime.now(timezone.utc).isoformat()

    result = await asyncio.to_thread(_run_ollama, request.model, request.prompt)

    duration_ms = (time.time() - start_time_unix) * 1000

    if result.returncode != 0:
        raise HTTPException(
            status_code=502,
            detail={
                "error": "Ollama run failed",
                "stderr": result.stderr or "(no stderr)",
                "return_code": result.returncode,
            },
        )

    return GenerateResponse(
        output=result.stdout or "",
        model=request.model,
        start_time_human=start_time_human,
        start_time_unix=start_time_unix,
        duration_ms=round(duration_ms, 2),
        duration_human=_format_duration_ms(duration_ms),
    )


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


static_dir = Path(__file__).parent / "static"


@app.get("/")
def index():
    """Serve the prompt test page."""
    index_file = static_dir / "index.html"
    if not index_file.is_file():
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(index_file)
