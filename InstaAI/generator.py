import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from renderer import render_carousel


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)

API_KEY = os.getenv("SENSENOVA_API_KEY")

if not API_KEY:
    raise ValueError("SENSENOVA_API_KEY not found in .env")


# ============================================================
# SENSENOVA CLIENT
# ============================================================

client = OpenAI(
    api_key=API_KEY,
    base_url="https://token.sensenova.ai/v1"
)

MODEL = "sensenova-6.8-flash-lite"


# ============================================================
# VISUAL TYPES
# ============================================================

ALLOWED_VISUAL_TYPES = {
    "hero",
    "comparison",
    "flowchart",
    "tools",
    "process",
    "cards",
    "equation"
}


# ============================================================
# GENERATE CAROUSEL
# ============================================================

def generate_carousel(topic):

    prompt = f"""
You are the content engine for "Lazy AI Engineer".

Create a beginner-friendly Instagram carousel about:

TOPIC:
{topic}

IMPORTANT:
Generate EXACTLY 7 slides.

The content must be:
- Beginner friendly
- Technically accurate
- Simple English
- Short and readable
- Useful for someone learning AI Engineering
- No unnecessary hype
- No fake claims

Each slide must contain:

1. slide_number
2. headline
3. body
4. visual_type
5. visual
6. visual_data

Allowed visual_type values:

hero
comparison
flowchart
tools
process
cards
equation


============================================================
VISUAL DATA RULES
============================================================

The "visual" field should briefly explain the visual.

The "visual_data" field MUST contain structured information
that the visual renderer can directly use.

Different visual types should use these structures:


HERO:

"visual_data": {{
    "center": "AI Agent",
    "left": "Goal",
    "right": "Action"
}}


COMPARISON:

"visual_data": {{
    "left_title": "Chatbot",
    "right_title": "AI Agent",
    "left_items": [
        "Answers questions",
        "Reactive",
        "No independent action"
    ],
    "right_items": [
        "Plans tasks",
        "Uses tools",
        "Takes action"
    ]
}}


FLOWCHART:

"visual_data": {{
    "steps": [
        "Perceive",
        "Plan",
        "Act",
        "Check"
    ]
}}


PROCESS:

"visual_data": {{
    "start": "Big Goal",
    "steps": [
        "Research",
        "Analyze",
        "Create"
    ],
    "end": "Completed Goal"
}}


TOOLS:

"visual_data": {{
    "center": "AI Agent",
    "tools": [
        "Browser",
        "Calculator",
        "Code",
        "Calendar"
    ]
}}


CARDS:

"visual_data": {{
    "cards": [
        {{
            "title": "Research",
            "description": "Find useful information"
        }},
        {{
            "title": "Coding",
            "description": "Write and debug code"
        }},
        {{
            "title": "Data",
            "description": "Analyze information"
        }},
        {{
            "title": "Automation",
            "description": "Complete repetitive tasks"
        }}
    ]
}}


EQUATION:

"visual_data": {{
    "terms": [
        "Language Model",
        "Tools",
        "Autonomy"
    ],
    "result": "AI Agent"
}}


============================================================
IMPORTANT
============================================================

The visual_data MUST match the actual slide content.

Do NOT use random generic examples.

For example, if the slide talks about:

Search
Calculator
Code Editor
Calendar

then visual_data.tools should contain those tools.

If the slide talks about:

Research
Coding
Travel
Email

then those should appear in visual_data.cards.

============================================================

Return ONLY valid JSON.

Use exactly this structure:

{{
    "slides": [
        {{
            "slide_number": 1,
            "headline": "string",
            "body": "string",
            "visual_type": "hero",
            "visual": "string",
            "visual_data": {{}}
        }}
    ]
}}
"""

    # ========================================================
    # API CALL
    # ========================================================

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a precise JSON content generator. "
                    "Return valid JSON only. "
                    "Do not use markdown."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.4
    )

    raw_content = response.choices[0].message.content.strip()

    # ========================================================
    # CLEAN JSON
    # ========================================================

    if raw_content.startswith("```"):
        raw_content = raw_content.replace("```json", "")
        raw_content = raw_content.replace("```", "")
        raw_content = raw_content.strip()

    try:
        data = json.loads(raw_content)

    except json.JSONDecodeError as e:

        print("\nERROR: SenseNova returned invalid JSON.\n")
        print(raw_content)

        raise ValueError(
            f"Could not parse SenseNova response as JSON: {e}"
        )


    # ========================================================
    # VALIDATE
    # ========================================================

    if "slides" not in data:
        raise ValueError("Response does not contain 'slides'.")

    slides = data["slides"]

    if len(slides) != 7:
        raise ValueError(
            f"Expected exactly 7 slides, received {len(slides)}."
        )


    for index, slide in enumerate(slides, start=1):

        required_fields = [
            "slide_number",
            "headline",
            "body",
            "visual_type",
            "visual",
            "visual_data"
        ]

        for field in required_fields:

            if field not in slide:
                raise ValueError(
                    f"Slide {index} is missing field: {field}"
                )

        visual_type = slide["visual_type"]

        if visual_type not in ALLOWED_VISUAL_TYPES:
            raise ValueError(
                f"Invalid visual_type on slide {index}: "
                f"{visual_type}"
            )


    # ========================================================
    # DISPLAY GENERATED CONTENT
    # ========================================================

    print("\n========================================")
    print("GENERATED 7-SLIDE CAROUSEL")
    print("========================================\n")

    for slide in slides:

        print(f"SLIDE {slide['slide_number']}")

        print(f"HEADLINE: {slide['headline']}")

        print(f"BODY: {slide['body']}")

        print(f"VISUAL TYPE: {slide['visual_type']}")

        print(f"VISUAL: {slide['visual']}")

        print(
            "VISUAL DATA:",
            json.dumps(
                slide["visual_data"],
                ensure_ascii=False
            )
        )

        print("----------------------------------------")


    # ========================================================
    # RENDER
    # ========================================================

    print("\nStarting visual renderer...\n")

    render_carousel(slides)

    print("\n========================================")
    print("7-SLIDE CAROUSEL GENERATED SUCCESSFULLY!")
    print("========================================")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    topic = input(
        "\nEnter Instagram carousel topic: "
    ).strip()

    if not topic:
        print("Topic cannot be empty.")
        raise SystemExit(1)

    generate_carousel(topic)