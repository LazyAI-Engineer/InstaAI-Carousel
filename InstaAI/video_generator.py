import re
import math
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

    # Main dark background
    background = ColorClip(
        size=(360, 640),
        color=(12, 14, 22),
        duration=audio.duration
    ).with_audio(audio)

    # --------------------------------------------------
    # AI VISUAL - UPPER HALF
    # --------------------------------------------------

    # Cyan glow behind AI text
    ai_glow = (
        TextClip(
            text="AI",
            font_size=94,
            color=(0, 190, 255),
            method="label",
            margin=(12, 12),
        )
        .with_duration(audio.duration)
        .with_opacity(0.18)
        .with_position(
            lambda t: (
                "center",
                125 + int(6 * math.sin(t * 0.8))
            )
        )
    )

    # Main AI title
    ai_title = (
        TextClip(
            text="AI",
            font_size=82,
            color="white",
            stroke_color=(0, 190, 255),
            stroke_width=2,
            method="label",
            margin=(10, 10),
        )
        .with_duration(audio.duration)
        .with_position(
            lambda t: (
                "center",
                130 + int(6 * math.sin(t * 0.8))
            )
        )
    )

    # Small technology label
    ai_subtitle = (
        TextClip(
            text="AI  •  LLM  •  AGENTS",
            font_size=17,
            color=(125, 220, 255),
            stroke_color="black",
            stroke_width=1,
            method="label",
            margin=(6, 6),
        )
        .with_duration(audio.duration)
        .with_position(
            ("center", 245)
        )
    )

    # --------------------------------------------------
    # FUTURISTIC CAPTION PANEL
    # --------------------------------------------------

    caption_panel = (
        ColorClip(
            size=(300, 105),
            color=(24, 32, 52),
            duration=audio.duration
        )
        .with_opacity(0.78)
        .with_position(
            ("center", 400)
        )
    )

    panel_highlight = (
        ColorClip(
            size=(290, 2),
            color=(0, 190, 255),
            duration=audio.duration
        )
        .with_opacity(0.75)
        .with_position(
            ("center", 407)
        )
    )

    # --------------------------------------------------
    # TOP-RIGHT BRANDING
    # --------------------------------------------------

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

    clips = [
        background,
        ai_glow,
        ai_title,
        ai_subtitle,
        caption_panel,
        panel_highlight,
        brand_clip
    ]

    caption_clips = []

    # --------------------------------------------------
    # WORD-BY-WORD CAPTIONS
    # --------------------------------------------------

    for start, end, text in read_srt(subtitle_file):

        caption = (
            TextClip(
                text=text,
                font_size=40,
                color="white",
                stroke_color="black",
                stroke_width=2,
                method="label",
                margin=(16, 16),
            )
            .with_start(start)
            .with_duration(
                max(
                    0.05,
                    end - start
                )
            )
            .with_position(
                ("center", 420)
            )
        )

        caption_clips.append(caption)
        clips.append(caption)

    # --------------------------------------------------
    # COMBINE VIDEO
    # --------------------------------------------------

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

    # --------------------------------------------------
    # CLEANUP
    # --------------------------------------------------

    for caption in caption_clips:
        caption.close()

    brand_clip.close()
    panel_highlight.close()
    caption_panel.close()
    ai_subtitle.close()
    ai_title.close()
    ai_glow.close()
    video.close()
    background.close()
    audio.close()

    return output_file
