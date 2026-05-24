import aiohttp
import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, Response
from fastapi.requests import Request
from contextlib import asynccontextmanager
from schema import ClientRequest, ResponseChunk, FinalChunk
from typing import cast
from cache import function_cache
from debug import DEBUG
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Server starting")
    timeout = aiohttp.ClientTimeout(total=None)
    client = aiohttp.ClientSession(timeout=timeout)
    app.state.client = client
    # Wait for server start
    yield 
    # Shutdown
    print("Shutting down server")
    await client.close()
app = FastAPI(lifespan=lifespan)
PORT = 11433
OLLAMA_PORT = 11434
OLLAMA_URL = f"http://localhost:{OLLAMA_PORT}"
@app.post("/api/show")
async def proxy(request: Request) -> Response:
    payload = await request.json()
    timeout = aiohttp.ClientTimeout(total=None)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(OLLAMA_URL, json=payload) as response:
            data = await response.text()
            return Response(content=data, media_type=response.content_type)

@app.post("/api/generate")
async def request_cache(request: Request) -> StreamingResponse:
    body: ClientRequest = await request.json()
    prompt = body["prompt"]
    cached_prompt = function_cache(prompt)
    body["prompt"] = cached_prompt
    if DEBUG:
        compare_diff(cached_prompt)
    async def stream():
        async with app.state.client.post(f"{OLLAMA_URL}/api/generate", json=body) as response:
            async for raw_line in response.content:
                if await request.is_disconnected():
                    break
                line = raw_line.decode().strip()
                if not line:
                    continue
                chunk: ResponseChunk = json.loads(line)
                if "done_reason" in chunk:
                    chunk = cast(FinalChunk, chunk)
                    line = line.rstrip() # Strip last line
                yield (line + "\n").encode()
    return StreamingResponse(stream(), media_type="application/x-ndjson")

if __name__ == "__main__":
    import uvicorn
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug",type=bool, default=False, help="Enable debug mode")
    parser.add_argument("--port", type=int, default=PORT, help="Server port")
    parser.add_argument("--ollama-port",  type=int, default=OLLAMA_PORT, help="Ollama port")
    
    args = parser.parse_args()
    
    DEBUG = args.debug
    PORT = args.port
    OLLAMA_PORT = args.ollama_port
    OLLAMA_URL = f"http://localhost:{OLLAMA_PORT}"
    
    if DEBUG:
        from debug import compare_diff
    
    uvicorn.run(app, port=11433)