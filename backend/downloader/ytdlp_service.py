import yt_dlp
import tempfile
import os
import uuid
import logging
import shutil

# Set up logging
logger = logging.getLogger("uvicorn")

# Map UI resolutions → yt-dlp format selectors (Best Quality / Merge)
MERGE_FORMATS = {
    "1080p": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best",
    "720p":  "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best",
    "360p":  "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]/best",
    "240p":  "bestvideo[height<=240][ext=mp4]+bestaudio[ext=m4a]/best[height<=240][ext=mp4]/best",
    "144p":  "bestvideo[height<=144][ext=mp4]+bestaudio[ext=m4a]/best[height<=144][ext=mp4]/best",
}

# Map UI resolutions → Single file formats (No FFmpeg needed)
SINGLE_FILE_FORMATS = {
    "1080p": "best[height<=1080][ext=mp4]/best",
    "720p":  "best[height<=720][ext=mp4]/best",
    "360p":  "best[height<=360][ext=mp4]/best",
    "240p":  "best[height<=240][ext=mp4]/best",
    "144p":  "best[height<=144][ext=mp4]/best",
}

def is_ffmpeg_available():
    """Check if ffmpeg is installed and in the system PATH"""
    return shutil.which('ffmpeg') is not None

def get_video_info(url: str):
    """Used to build the download table"""
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    return {
        "title": info.get("title"),
        "thumbnail": info.get("thumbnail"),
        "duration": info.get("duration_string"),
        "platform": info.get("extractor_key"),
    }

def download_video(url: str, resolution: str):
    """Downloads the video to a temporary file and returns the path"""
    
    # 1. Check for FFmpeg first
    has_ffmpeg = is_ffmpeg_available()
    
    if has_ffmpeg:
        # Use high-quality merge formats
        format_selector = MERGE_FORMATS.get(resolution, "best")
        logger.info(f"FFmpeg detected. Using merge format for {resolution}")
    else:
        # Use safe single-file formats (prevents 'ffmpeg not installed' error)
        format_selector = SINGLE_FILE_FORMATS.get(resolution, "best[ext=mp4]/best")
        logger.warning(f"FFmpeg not found. Using single-file format for {resolution} to prevent errors.")
    
    # Use a temp directory
    temp_dir = tempfile.gettempdir()
    unique_id = str(uuid.uuid4())[:8]
    
    # Options
    ydl_opts = {
        'outtmpl': os.path.join(temp_dir, f'%(title)s_{unique_id}.%(ext)s'),
        'restrictfilenames': True, 
        'quiet': True,
        'noplaylist': True,
        'format': format_selector,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename
            
    except Exception as e:
        logger.error(f"Download failed: {e}")
        # If it failed even with single file format, we can't do much else
        raise e