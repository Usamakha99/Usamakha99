
from pathlib import Path
from html import escape
from PIL import Image, ImageOps, ImageEnhance

# Input and output paths
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_IMAGE = BASE_DIR / "profile-photo.jpg"
OUTPUT_SVG = BASE_DIR / "usama-ascii.svg"

# ASCII portrait settings
COLUMNS = 100
CHAR_WIDTH = 8
LINE_HEIGHT = 12
RAMP = " .`:-=+*cs#%@"
TEXT_COLOR = "#c9d1d9"
BACKGROUND = "#0d1117"


def main():
    if not INPUT_IMAGE.exists():
        raise FileNotFoundError(
            f"Photo not found: {INPUT_IMAGE}\n"
            "Place your original photo at the repository root "
            "as profile-photo.jpg."
        )

    image = Image.open(INPUT_IMAGE).convert("RGB")

    # Resize while accounting for the height of monospace characters.
    width, height = image.size
    rows = max(1, round(height * COLUMNS * CHAR_WIDTH / width / LINE_HEIGHT))
    image = image.resize((COLUMNS, rows), Image.Resampling.LANCZOS)

    gray = ImageOps.grayscale(image)
    gray = ImageEnhance.Contrast(gray).enhance(1.5)

    ascii_rows = []
    for y in range(rows):
        line = ""
        for x in range(COLUMNS):
            brightness = gray.getpixel((x, y))
            index = round(
                (255 - brightness) * (len(RAMP) - 1) / 255
            )
            line += RAMP[index]
        ascii_rows.append(line)

    svg_width = COLUMNS * CHAR_WIDTH
    svg_height = rows * LINE_HEIGHT + 24
    animation_duration = 1.8
    row_delay = 0.045

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{svg_width}" height="{svg_height}" '
        f'viewBox="0 0 {svg_width} {svg_height}">',
        f'<rect width="100%" height="100%" fill="{BACKGROUND}"/>',
        f'<g fill="{TEXT_COLOR}" font-family="Consolas, '
        f'Menlo, monospace" font-size="10" '
        f'textLength="{svg_width}" lengthAdjust="spacingAndGlyphs" '
        f'xml:space="preserve">'
    ]

    for y, line in enumerate(ascii_rows):
        clip_id = f"row-{y}"
        ypos = 14 + y * LINE_HEIGHT
        delay = y * row_delay

        parts.append(
            f'<clipPath id="{clip_id}">'
            f'<rect x="0" y="{ypos - 10}" width="0" '
            f'height="{LINE_HEIGHT}">'
            f'<animate attributeName="width" '
            f'from="0" to="{svg_width}" '
            f'dur="{animation_duration}s" '
            f'begin="{delay:.3f}s" fill="freeze"/>'
            f'</rect></clipPath>'
        )

        parts.append(
            f'<text x="0" y="{ypos}" '
            f'clip-path="url(#{clip_id})">'
            f'{escape(line)}'
            f'</text>'
        )

    parts.append("</g></svg>")

    # Keep clip definitions outside the rendered text group.
    svg = parts[0] + parts[1] + "<defs>" + "".join(
        part for part in parts[2:] if part.startswith("<clipPath")
    ) + "</defs><g " + parts[2].split("<g ", 1)[1]

    svg += "".join(
        part for part in parts[2:] if part.startswith("<text")
    )
    svg += "</g></svg>"

    OUTPUT_SVG.write_text(svg, encoding="utf-8")
    print(f"ASCII portrait created: {OUTPUT_SVG}")
    print(f"Grid: {COLUMNS} columns x {rows} rows")


if __name__ == "__main__":
    main()
