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
        size=(1080, 1920),
        color=(15, 15, 20),
        duration=audio.duration
    )

    video = video.with_audio(audio)

    video.write_videofile(
        output_file,
        fps=30,
        codec="libx264",
        audio_codec="aac"
    )

    audio.close()
    video.close()

    return output_file
