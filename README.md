# Ollama API

REST API server that runs [Ollama](https://ollama.ai) models via HTTP. Handles concurrent requests without blocking.

## Prerequisites

- [Ollama](https://ollama.ai) installed and running
- Python 3.9+
- A model pulled (e.g. `ollama pull gpt-oss:20b`)

## Setup

```bash
./setup.sh
```

Creates a virtual environment, installs dependencies from `requirements.txt`, and upgrades pip.

## Run

```bash
./run.sh
```

Starts the server at `http://0.0.0.0:8000`. Use `./run.sh --reload` for development.

## API

### POST /generate

Generate text from a prompt.

**Request (JSON):**

| Field   | Type   | Required | Default       | Description        |
|---------|--------|----------|---------------|--------------------|
| prompt  | string | yes      | —             | Text prompt        |
| model   | string | no       | `gpt-oss:20b` | Ollama model name  |

**Response (JSON):**

- `output` — generated text
- `model` — model used

**Example:**

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, how are you?"}'
```

### GET /health

Health check. Returns `{"status": "ok"}`.

## Docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
