from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response, StreamingResponse
import httpx
import os
from pathlib import Path
from dotenv import load_dotenv


# ============================================================
# LOAD PROJECT .ENV
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

load_dotenv(
    PROJECT_ROOT / ".env",
    override=True
)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI()


# ============================================================
# OLLAMA CONFIGURATION
# ============================================================

OLLAMA_URL = "http://127.0.0.1:11434"

OLLAMA_TOKEN = os.getenv("OLLAMA_PROXY_TOKEN")


if not OLLAMA_TOKEN:
    raise RuntimeError(
        "OLLAMA_PROXY_TOKEN is not set"
    )


# ============================================================
# AUTHENTICATION
# ============================================================

def check_auth(request: Request):

    auth = request.headers.get("Authorization")

    if auth != f"Bearer {OLLAMA_TOKEN}":

        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )


# ============================================================
# PROXY ROUTE
# ============================================================

@app.api_route(
    "/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE"
    ]
)
async def proxy(
    path: str,
    request: Request
):

    # --------------------------------------------------------
    # Check incoming authentication
    # --------------------------------------------------------

    check_auth(request)


    # --------------------------------------------------------
    # Build Ollama URL
    # --------------------------------------------------------

    url = f"{OLLAMA_URL}/{path}"


    # --------------------------------------------------------
    # Read request body
    # --------------------------------------------------------

    body = await request.body()


    # --------------------------------------------------------
    # Forward headers
    # Remove headers that should not be forwarded
    # --------------------------------------------------------

    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in {
            "host",
            "content-length",
            "authorization"
        }
    }


    # --------------------------------------------------------
    # Create HTTP client
    # --------------------------------------------------------

    client = httpx.AsyncClient(
        timeout=None
    )


    try:

        # ----------------------------------------------------
        # Build request to Ollama
        # ----------------------------------------------------

        upstream_request = client.build_request(
            method=request.method,
            url=url,
            content=body,
            headers=headers
        )


        # ----------------------------------------------------
        # Send request to Ollama
        # ----------------------------------------------------

        response = await client.send(
            upstream_request,
            stream=True
        )


        # ----------------------------------------------------
        # Handle upstream errors
        # ----------------------------------------------------

        if response.status_code >= 400:

            content = await response.aread()

            await response.aclose()
            await client.aclose()

            return Response(
                content=content,
                status_code=response.status_code,
                media_type=response.headers.get(
                    "content-type"
                )
            )


        # ----------------------------------------------------
        # Stream response from Ollama
        # ----------------------------------------------------

        async def stream_response():

            try:

                async for chunk in response.aiter_raw():

                    yield chunk

            finally:

                await response.aclose()
                await client.aclose()


        # ----------------------------------------------------
        # Return streaming response
        # ----------------------------------------------------

        return StreamingResponse(
            stream_response(),
            status_code=response.status_code,
            media_type=response.headers.get(
                "content-type"
            )
        )


    except Exception:

        await client.aclose()

        raise