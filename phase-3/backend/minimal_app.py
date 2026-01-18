"""Minimal FastAPI app to test if basic server works."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse

app = FastAPI(title="Minimal Test App")


@app.get("/")
async def root():
    return {"message": "Hello from minimal app"}


@app.get("/ping")
async def ping():
    return PlainTextResponse("pong")


@app.get("/health")
async def health():
    return JSONResponse({"status": "healthy"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
