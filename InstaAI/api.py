from video_generator import generate_voice
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from generator import generate_carousel


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="InstaAI Carousel API")

app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")


class GenerateRequest(BaseModel):
    topic: str


@app.get("/")
def home():
    return {
        "status": "ok",
        "service": "InstaAI Carousel API"
    }


@app.post("/generate")
def generate(data: GenerateRequest, request: Request):
    topic = data.topic.strip()

    if not topic:
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")

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
        raise HTTPException(status_code=500, detail=str(e))
        class VoiceRequest(BaseModel):
    text: str


@app.post("/generate-voice")
def generate_voice_api(data: VoiceRequest, request: Request):
    try:
        output_file = str(OUTPUT_DIR / "voice.mp3")

        generate_voice(
            data.text,
            output_file
        )

        base_url = str(request.base_url).rstrip("/")

        return {
            "status": "success",
            "audio_url": f"{base_url}/outputs/voice.mp3"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
