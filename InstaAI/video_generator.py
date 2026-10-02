import asyncio
import edge_tts


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
