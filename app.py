import logging
import uvicorn

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.routers.recognition_router import router as recognition_router
from src.routers.user_router import router as user_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

app = FastAPI(
    title="Face Recognition API",
    version="1.0.0"
)

# static frontend
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# routers
app.include_router(recognition_router)
app.include_router(user_router)


@app.get("/")
def root():
    return {"message": "Face Recognition API Running"}


@app.get("/ui")
def ui():
    return FileResponse("frontend/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )