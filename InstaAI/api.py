from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from generator import generate_carousel
from video_generator import (
    generate_voice,
    generate_simple_video,
    generate_voice_with_subtitles,
    generate_captioned_video,
)


# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# FASTAPI APP
# --------------------------------------------------

app = FastAPI(title="InstaAI Carousel API")

app.mount(
    "/outputs",
    StaticFiles(directory=str(OUTPUT_DIR)),
    name="outputs"
)


# --------------------------------------------------
# REQUEST MODELS
# --------------------------------------------------

class GenerateRequest(BaseModel):
    topic: str


class VoiceRequest(BaseModel):
    text: str


class VideoRequest(BaseModel):
    text: str


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "status": "ok",
        "service": "InstaAI Carousel API"
    }


# --------------------------------------------------
# CAROUSEL GENERATION
# --------------------------------------------------

@app.post("/generate")
def generate(data: GenerateRequest, request: Request):
    topic = data.topic.strip()

    if not topic:
        raise HTTPException(
            status_code=400,
            detail="Topic cannot be empty."
        )

    try:
        slides = generate_carousel(topic)

        base_url = str(request.base_url).rstrip("/")

        image_urls = [
            f"{base_url}/outputs/slide_{i}.png"
            for i in range(1, 8)
        ]

        return {
            "status": "success",
            "topic": topic,
            "slides": slides,
            "images": image_urls
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# --------------------------------------------------
# VOICE GENERATION
# --------------------------------------------------

@app.post("/generate-voice")
def generate_voice_api(
    data: VoiceRequest,
    request: Request
):
    text = data.text.strip()

    if not text:
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty."
        )

    try:
        file_id = uuid4().hex[:12]

        audio_name = f"voice_{file_id}.mp3"
        audio_file = str(
            OUTPUT_DIR / audio_name
        )

        generate_voice(
            text,
            audio_file
        )

        base_url = str(request.base_url).rstrip("/")

        return {
            "status": "success",
            "audio_url": (
                f"{base_url}/outputs/{audio_name}"
            )
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# --------------------------------------------------
# VIDEO GENERATION
# --------------------------------------------------

@app.post("/generate-video")
def generate_video_api(
    data: VideoRequest,
    request: Request
):
    text = data.text.strip()

    if not text:
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty."
        )

    try:
        # Unique ID for this video generation
        file_id = uuid4().hex[:12]

        audio_name = (
            f"short_voice_{file_id}.mp3"
        )

        subtitle_name = (
            f"captions_{file_id}.srt"
        )

        video_name = (
            f"short_{file_id}.mp4"
        )

        audio_file = str(
            OUTPUT_DIR / audio_name
        )

        subtitle_file = str(
            OUTPUT_DIR / subtitle_name
        )

        video_file = str(
            OUTPUT_DIR / video_name
        )

        # Create voice + word timestamps
        generate_voice_with_subtitles(
            text,
            audio_file,
            subtitle_file
        )

        # Create final branded captioned video
        generate_captioned_video(
            audio_file,
            subtitle_file,
            video_file
        )

        base_url = str(
            request.base_url
        ).rstrip("/")

        return {
            "status": "success",

            "id": file_id,

            "video_url": (
                f"{base_url}/outputs/"
                f"{video_name}"
            ),

            "audio_url": (
                f"{base_url}/outputs/"
                f"{audio_name}"
            ),

            "captions_url": (
                f"{base_url}/outputs/"
                f"{subtitle_name}"
            )
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
