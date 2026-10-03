import re
import asyncio
import edge_tts

from moviepy import (
    ColorClip,
    AudioFileClip,
    TextClip,
    CompositeVideoClip,
)


# --------------------------------------------------
# BASIC VOICE GENERATION
# --------------------------------------------------

async def make_voice(text, output_file="voice.mp3"):
    voice = "en-IN-NeerjaNeural"

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice
    )

    await communicate.save(output_file)

    return output_file


def generate_voice(text, output_file="voice.mp3"):
    return asyncio.run(
        make_voice(
            text,
            output_file
        )
    )


# --------------------------------------------------
# BASIC VIDEO GENERATION
# --------------------------------------------------

def generate_simple_video(
    audio_file,
    output_file="short.mp4"
):
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

    video.close()
    audio.close()

    return output_file


# --------------------------------------------------
# VOICE + WORD TIMESTAMPS
# --------------------------------------------------

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

    with open(
        subtitle_file,
        "w",
        encoding="utf-8"
    ) as subtitles:
        subtitles.write(
            submaker.get_srt()
        )

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


# --------------------------------------------------
# SRT READER
# --------------------------------------------------

def srt_time_to_seconds(timestamp):
    hours, minutes, rest = timestamp.split(":")
    seconds, milliseconds = rest.split(",")

    return (
        int(hours) * 3600
        + int(minutes) * 60
        + int(seconds)
        + int(milliseconds) / 1000
    )


def read_srt(subtitle_file):
    with open(
        subtitle_file,
        "r",
        encoding="utf-8"
    ) as file:
        content = file.read().strip()

    blocks = re.split(
        r"\n\s*\n",
        content
    )

    captions = []

    for block in blocks:
        lines = block.splitlines()

        if len(lines) < 3:
            continue

        times = lines[1].split(" --> ")

        start = srt_time_to_seconds(
            times[0].strip()
        )

        end = srt_time_to_seconds(
            times[1].strip()
        )

        text = " ".join(
            lines[2:]
        ).strip()

        captions.append(
            (start, end, text)
        )

    return captions


# --------------------------------------------------
# CAPTIONED + BRANDED SHORT VIDEO
# --------------------------------------------------

def generate_captioned_video(
    audio_file,
    subtitle_file,
    output_file="short.mp4"
):
    audio = AudioFileClip(audio_file)

    background = ColorClip(
        size=(360, 640),
        color=(15, 15, 20),
        duration=audio.duration
    ).with_audio(audio)

   brand_clip = TextClip(
    text="@Lazy AI Engineer",
    font_size=16,
    color="white",
    stroke_color="black",
    stroke_width=1,
    method="label",
    margin=(6, 6),
)

brand_clip = (
    brand_clip
    .with_start(0)
    .with_duration(audio.duration)
    .with_position(
        (360 - brand_clip.w - 12, 18)
    )
)

    clips = [background, brand_clip]
    caption_clips = [brand_clip]

    for start, end, text in read_srt(subtitle_file):

        caption = (
            TextClip(
                text=text,
                font_size=44,
                color="white",
                stroke_color="black",
                stroke_width=2,
                method="label",
                margin=(20, 20),
            )
            .with_start(start)
            .with_duration(max(0.05, end - start))
            .with_position(("center", 430))
        )

        caption_clips.append(caption)
        clips.append(caption)

    video = CompositeVideoClip(
        clips,
        size=(360, 640)
    )

    video.write_videofile(
        output_file,
        fps=15,
        codec="libx264",
        audio_codec="aac"
    )

    for clip in caption_clips:
        clip.close()

    video.close()
    background.close()
    audio.close()

    return output_file
