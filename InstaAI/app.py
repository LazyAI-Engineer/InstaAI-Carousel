import os
import sys
from pathlib import Path

from generator import generate_carousel


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"


# ============================================================
# UI HELPERS
# ============================================================

def print_header():
    print("\n")
    print("=" * 58)
    print("              LAZY AI ENGINEER")
    print("          INSTAAI CAROUSEL GENERATOR")
    print("=" * 58)

    print(
        "\nCreate a complete 7-slide Instagram carousel"
        "\nfrom a single topic."
    )

    print("\nOutput:")
    print("• 7 separate PNG images")
    print("• 1080 × 1350")
    print("• Instagram 4:5 format")
    print("• Saved inside InstaAI/outputs/")

    print("\n" + "-" * 58)


def print_success():
    print("\n")
    print("=" * 58)
    print("              CAROUSEL READY")
    print("=" * 58)

    print("\nGenerated files:\n")

    for number in range(1, 8):
        file_path = OUTPUT_DIR / f"slide_{number}.png"

        if file_path.exists():
            print(f"✓ slide_{number}.png")
        else:
            print(f"✗ slide_{number}.png missing")

    print(f"\nOutput folder:\n{OUTPUT_DIR}")

    print("\n" + "=" * 58)


def clear_old_slides():
    """
    Remove old generated slides before creating a new carousel.

    This prevents old PNG files from being mistaken for
    newly generated slides if generation fails halfway.
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    removed = 0

    for number in range(1, 8):
        file_path = OUTPUT_DIR / f"slide_{number}.png"

        if file_path.exists():
            file_path.unlink()
            removed += 1

    if removed:
        print(f"\nRemoved {removed} old slide(s).")


def verify_outputs():
    """
    Confirm that all seven slides were actually generated.
    """

    missing = []

    for number in range(1, 8):
        file_path = OUTPUT_DIR / f"slide_{number}.png"

        if not file_path.exists():
            missing.append(file_path.name)

    if missing:
        raise RuntimeError(
            "Carousel generation finished, but these files "
            "are missing:\n"
            + "\n".join(missing)
        )


# ============================================================
# GENERATE
# ============================================================

def create_carousel(topic):
    print("\n" + "=" * 58)
    print("STARTING CAROUSEL GENERATION")
    print("=" * 58)

    print(f"\nTopic:\n{topic}")

    print("\nStep 1/4  Cleaning previous output...")
    clear_old_slides()

    print("\nStep 2/4  Generating carousel content with AI...")

    generate_carousel(topic)

    print("\nStep 3/4  Checking generated files...")

    verify_outputs()

    print("\nStep 4/4  Complete.")

    print_success()


# ============================================================
# MAIN APP
# ============================================================

def main():
    print_header()

    while True:

        topic = input(
            "\nEnter carousel topic"
            "\n(or type 'exit' to close):\n\n> "
        ).strip()

        if not topic:
            print("\n⚠ Topic cannot be empty.")
            continue

        if topic.lower() in {"exit", "quit", "q"}:
            print("\nClosing InstaAI. Goodbye!\n")
            break

        try:

            create_carousel(topic)

        except KeyboardInterrupt:

            print("\n\nGeneration cancelled.")
            break

        except Exception as error:

            print("\n")
            print("=" * 58)
            print("              GENERATION FAILED")
            print("=" * 58)

            print(f"\nError:\n{error}")

            print(
                "\nYour API key, internet connection, "
                "SenseNova response, or renderer may need checking."
            )

            print("\nNo successful carousel was reported.")

        print("\n" + "-" * 58)

        again = input(
            "\nCreate another carousel? (y/n): "
        ).strip().lower()

        if again not in {"y", "yes"}:
            print("\nClosing InstaAI. Goodbye!\n")
            break


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()