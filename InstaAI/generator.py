import os
import json

from dotenv import load_dotenv
from openai import OpenAI

from prompts import CAROUSEL_SYSTEM_PROMPT, build_carousel_prompt
from renderer import render_carousel


# ============================================================
# PATHS / ENVIRONMENT
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)

API_KEY = os.getenv("SENSENOVA_API_KEY")

if not API_KEY:
    raise ValueError(
        "SENSENOVA_API_KEY not found in InstaAI/.env"
    )


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
    "equation",
}


# ============================================================
# VALIDATION HELPERS
# ============================================================

def require_non_empty_string(slide, field, slide_number):
    """
    Confirm that a required text field exists and is not empty.
    """

    value = slide.get(field)

    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"Slide {slide_number}: '{field}' "
            "must be a non-empty string."
        )


def require_string_list(
    data,
    field,
    slide_number,
    minimum=1,
):
    """
    Confirm that visual_data contains a usable list of strings.
    """

    value = data.get(field)

    if not isinstance(value, list) or len(value) < minimum:
        raise ValueError(
            f"Slide {slide_number}: visual_data['{field}'] "
            f"must contain at least {minimum} item(s)."
        )

    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(
                f"Slide {slide_number}: "
                f"visual_data['{field}'] contains "
                "an invalid item."
            )


def validate_visual_data(slide, slide_number):
    """
    Validate visual_data according to visual_type.
    """

    visual_type = slide["visual_type"]
    data = slide["visual_data"]

    if not isinstance(data, dict):
        raise ValueError(
            f"Slide {slide_number}: visual_data "
            "must be a JSON object."
        )

    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    if visual_type == "hero":

        for field in ("center", "left", "right"):
            value = data.get(field)

            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"Slide {slide_number}: hero visual "
                    f"is missing '{field}'."
                )

    # --------------------------------------------------------
    # COMPARISON
    # --------------------------------------------------------

    elif visual_type == "comparison":

        for field in ("left_title", "right_title"):
            value = data.get(field)

            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"Slide {slide_number}: comparison "
                    f"is missing '{field}'."
                )

        require_string_list(
            data,
            "left_items",
            slide_number,
            minimum=1,
        )

        require_string_list(
            data,
            "right_items",
            slide_number,
            minimum=1,
        )

    # --------------------------------------------------------
    # FLOWCHART
    # --------------------------------------------------------

    elif visual_type == "flowchart":

        require_string_list(
            data,
            "steps",
            slide_number,
            minimum=2,
        )

    # --------------------------------------------------------
    # PROCESS
    # --------------------------------------------------------

    elif visual_type == "process":

        for field in ("start", "end"):
            value = data.get(field)

            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"Slide {slide_number}: process visual "
                    f"is missing '{field}'."
                )

        require_string_list(
            data,
            "steps",
            slide_number,
            minimum=1,
        )

    # --------------------------------------------------------
    # TOOLS
    # --------------------------------------------------------

    elif visual_type == "tools":

        center = data.get("center")

        if not isinstance(center, str) or not center.strip():
            raise ValueError(
                f"Slide {slide_number}: tools visual "
                "is missing 'center'."
            )

        require_string_list(
            data,
            "tools",
            slide_number,
            minimum=1,
        )

    # --------------------------------------------------------
    # CARDS
    # --------------------------------------------------------

    elif visual_type == "cards":

        cards = data.get("cards")

        if not isinstance(cards, list) or not cards:
            raise ValueError(
                f"Slide {slide_number}: cards visual "
                "requires a non-empty 'cards' list."
            )

        for card_index, card in enumerate(cards, start=1):

            if not isinstance(card, dict):
                raise ValueError(
                    f"Slide {slide_number}: card "
                    f"{card_index} must be an object."
                )

            for field in ("title", "description"):

                value = card.get(field)

                if not isinstance(value, str) or not value.strip():
                    raise ValueError(
                        f"Slide {slide_number}: card "
                        f"{card_index} is missing '{field}'."
                    )

    # --------------------------------------------------------
    # EQUATION
    # --------------------------------------------------------

    elif visual_type == "equation":

        require_string_list(
            data,
            "terms",
            slide_number,
            minimum=2,
        )

        result = data.get("result")

        if not isinstance(result, str) or not result.strip():
            raise ValueError(
                f"Slide {slide_number}: equation visual "
                "is missing 'result'."
            )


def validate_carousel(data):
    """
    Validate the complete AI-generated carousel before rendering.
    """

    if not isinstance(data, dict):
        raise ValueError(
            "SenseNova response must be a JSON object."
        )

    if "slides" not in data:
        raise ValueError(
            "SenseNova response does not contain 'slides'."
        )

    slides = data["slides"]

    if not isinstance(slides, list):
        raise ValueError(
            "'slides' must be a list."
        )

    if len(slides) != 7:
        raise ValueError(
            f"Expected exactly 7 slides, "
            f"received {len(slides)}."
        )

    required_fields = (
        "slide_number",
        "headline",
        "body",
        "visual_type",
        "visual",
        "visual_data",
    )

    for index, slide in enumerate(slides, start=1):

        if not isinstance(slide, dict):
            raise ValueError(
                f"Slide {index} must be a JSON object."
            )

        for field in required_fields:

            if field not in slide:
                raise ValueError(
                    f"Slide {index} is missing "
                    f"required field: {field}"
                )

        # Make sure numbering is exactly 1 → 7

        if slide["slide_number"] != index:
            raise ValueError(
                f"Slide {index}: expected slide_number "
                f"{index}, received "
                f"{slide['slide_number']}."
            )

        # Validate text

        require_non_empty_string(
            slide,
            "headline",
            index,
        )

        require_non_empty_string(
            slide,
            "body",
            index,
        )

        require_non_empty_string(
            slide,
            "visual",
            index,
        )

        # Validate visual type

        visual_type = slide["visual_type"]

        if visual_type not in ALLOWED_VISUAL_TYPES:
            raise ValueError(
                f"Slide {index}: invalid visual_type "
                f"'{visual_type}'."
            )

        # Validate renderer data

        validate_visual_data(
            slide,
            index,
        )

    return slides


# ============================================================
# CLEAN MODEL RESPONSE
# ============================================================

def parse_model_response(raw_content):
    """
    Convert SenseNova response into Python data.
    """

    if not raw_content:
        raise ValueError(
            "SenseNova returned an empty response."
        )

    raw_content = raw_content.strip()

    # Defensive cleanup in case the model ignores
    # the instruction and returns a Markdown code block.

    if raw_content.startswith("```"):

        raw_content = raw_content.replace(
            "```json",
            "",
            1,
        )

        raw_content = raw_content.replace(
            "```JSON",
            "",
            1,
        )

        raw_content = raw_content.replace(
            "```",
            "",
        )

        raw_content = raw_content.strip()

    try:
        return json.loads(raw_content)

    except json.JSONDecodeError as error:

        print("\nERROR: SenseNova returned invalid JSON.\n")
        print(raw_content)

        raise ValueError(
            "Could not parse SenseNova response "
            f"as JSON: {error}"
        ) from error


# ============================================================
# DISPLAY CONTENT
# ============================================================

def display_carousel(slides):

    print("\n")
    print("=" * 58)
    print("GENERATED 7-SLIDE CAROUSEL")
    print("=" * 58)

    for slide in slides:

        print(
            f"\nSLIDE {slide['slide_number']}"
        )

        print(
            f"HEADLINE: {slide['headline']}"
        )

        print(
            f"BODY: {slide['body']}"
        )

        print(
            f"VISUAL TYPE: {slide['visual_type']}"
        )

        print(
            f"VISUAL: {slide['visual']}"
        )

        print(
            "VISUAL DATA:",
            json.dumps(
                slide["visual_data"],
                ensure_ascii=False,
            ),
        )

        print("-" * 58)


# ============================================================
# GENERATE CAROUSEL
# ============================================================

def generate_carousel(topic):

    if not isinstance(topic, str) or not topic.strip():
        raise ValueError(
            "Carousel topic cannot be empty."
        )

    topic = topic.strip()

    # --------------------------------------------------------
    # BUILD PROMPTS
    # --------------------------------------------------------

    user_prompt = build_carousel_prompt(topic)

    # --------------------------------------------------------
    # API CALL
    # --------------------------------------------------------

    print("\nContacting SenseNova...")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": CAROUSEL_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0.4,
    )

    # --------------------------------------------------------
    # READ RESPONSE
    # --------------------------------------------------------

    if not response.choices:
        raise ValueError(
            "SenseNova returned no response choices."
        )

    raw_content = (
        response
        .choices[0]
        .message
        .content
    )

    # --------------------------------------------------------
    # PARSE
    # --------------------------------------------------------

    data = parse_model_response(
        raw_content
    )

    # --------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------

    print("Validating 7-slide structure...")

    slides = validate_carousel(
        data
    )

    print("Validation passed.")

    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    display_carousel(
        slides
    )

    # --------------------------------------------------------
    # RENDER
    # --------------------------------------------------------

    print("\nStarting visual renderer...\n")

    render_carousel(
        slides
    )

    print("\n")
    print("=" * 58)
    print("7-SLIDE CAROUSEL GENERATED SUCCESSFULLY!")
    print("=" * 58)

    return slides


# ============================================================
# DIRECT RUN
# ============================================================

if __name__ == "__main__":

    topic = input(
        "\nEnter Instagram carousel topic: "
    ).strip()

    if not topic:
        print("Topic cannot be empty.")
        raise SystemExit(1)

    try:

        generate_carousel(
            topic
        )

    except Exception as error:

        print("\nGENERATION FAILED")
        print(f"\n{error}")

        raise SystemExit(1)