import asyncio
import edge_tts
from moviepy import ColorClip, AudioFileClip


async def make_voice(text, output_file="voice.mp3"):
    voice = "en-IN-NeerjaNeural"

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice
    )

    await communicate.save(output_file)
    return output_file


def generate_voice(text, output_file="voice.mp3"):
    return asyncio.run(make_voice(text, output_file))


def generate_simple_video(audio_file, output_file="short.mp4"):
    audio = AudioFileClip(audio_file)

    video = ColorClip(
        size=(360, 640),
        color=(15, 15, 20),
        duration=audio.duration
    )

    video = video.with_audio(audio)

    video.write_videofile(
        output_file,
        fps=15,
        codec="libx264",
        audio_codec="aac"
    )

    audio.close()
    video.close()

    return output_file
async def make_voice_with_subtitles(
    text,
    audio_file="voice.mp3",
    subtitle_file="captions.srt"
):
    voice = "en-IN-NeerjaNeural"

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        boundary="WordBoundary"
    )

    submaker = edge_tts.SubMaker()

    with open(audio_file, "wb") as audio:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio.write(chunk["data"])

            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)

    with open(subtitle_file, "w", encoding="utf-8") as subtitles:
        subtitles.write(submaker.get_srt())

    return audio_file, subtitle_file


def generate_voice_with_subtitles(
    text,
    audio_file="voice.mp3",
    subtitle_file="captions.srt"
):
    return asyncio.run(
        make_voice_with_subtitles(
            text,
            audio_file,
            subtitle_file
        )
    )
