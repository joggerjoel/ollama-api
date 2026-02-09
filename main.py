import asyncio
import subprocess

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Ollama Generate API", version="1.0.0")


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="The text prompt to send to the model")
    model: str = Field(default="gpt-oss:20b", description="Ollama model name to use")


class GenerateResponse(BaseModel):
    output: str = Field(..., description="Generated text from the model")
    model: str = Field(..., description="Model that was used")


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
    result = await asyncio.to_thread(_run_ollama, request.model, request.prompt)

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
    )


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}
