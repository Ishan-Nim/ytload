from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import logging
import uvicorn

from schemas.video import VideoRequest
from downloader.ytdlp_service import get_video_info, download_video

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")

app = FastAPI(title="MediaSaver API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def remove_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
            logger.info(f"Cleaned up file: {path}")
    except Exception as e:
        logger.error(f"Error removing file {path}: {e}")

@app.get("/")
def root():
    return {"status": "MediaSaver API running"}

@app.post("/api/video-info")
def fetch_video_info(payload: VideoRequest):
    try:
        return get_video_info(str(payload.url))
    except Exception as e:
        logger.error(f"Info fetch error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/download")
def download(payload: dict, background_tasks: BackgroundTasks):
    url = payload.get("url")
    resolution = payload.get("resolution")

    if not url or not resolution:
        raise HTTPException(status_code=400, detail="Missing parameters")

    try:
        logger.info(f"Received download request for: {url} [{resolution}]")
        
        # This is a synchronous call (blocking), but okay for this simple app
        file_path = download_video(url, resolution)
        
        if not os.path.exists(file_path):
             logger.error(f"File not found at {file_path}")
             raise HTTPException(status_code=500, detail="File download failed")
             
        filename = os.path.basename(file_path)
        
        # Schedule file removal after response is sent
        background_tasks.add_task(remove_file, file_path)
        
        return FileResponse(
            file_path,
            media_type="application/octet-stream",
            filename=filename,
        )
    except Exception as e:
        logger.error(f"Download Error: {e}")
        raise HTTPException(status_code=400, detail=f"Download failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)