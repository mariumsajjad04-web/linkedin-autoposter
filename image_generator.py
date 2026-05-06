"""
Generate a Canva-style quote card image for each LinkedIn post.
Uses PIL only — no external API, zero cost, works on GitHub Actions.
"""
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont


# ============================================================
# DESIGN PRESETS — rotate randomly for variety
# ============================================================
TEMPLATES = [
    {
        "name": "deep_purple",
        "bg_top": (88, 28, 135),       # Deep purple
        "bg_bottom": (30, 27, 75),     # Almost black
        "accent": (250, 204, 21),      # Yellow
        "text_color": (255, 255, 255),
    },
    {
        "name": "ocean",
        "bg_top": (15, 23, 42),        # Slate-900
        "bg_bottom": (30, 64, 175),    # Blue-800
        "accent": (34, 211, 238),      # Cyan
        "text_color": (255, 255, 255),
    },
    {
        "name": "sunset",
        "bg_top": (124, 45, 18),       # Orange-900
        "bg_bottom": (88, 28, 135),    # Purple-900
        "accent": (251, 191, 36),      # Amber
        "text_color": (255, 255, 255),
    },
    {
        "name": "forest",
        "bg_top": (6, 78, 59),         # Emerald-900
        "bg_bottom": (15, 23, 42),     # Slate-900
        "accent": (52, 211, 153),      # Emerald-400
        "text_color": (255, 255, 255),
    },
    {
        "name": "minimal_dark",
        "bg_top": (10, 10, 10),
        "bg_bottom": (40, 40, 40),
        "accent": (255, 255, 255),
        "text_color": (255, 255, 255),
    },
]


def find_font(size, bold=False):
    """Find a usable system font that supports the requested weight."""
    candidates_bold = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\seguibl.ttf",
    ]
    candidates_regular = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\segoeui.ttf",
    ]
    paths = candidates_bold if bold else candidates_regular
    for path in paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def make_gradient(width, height, top_color, bottom_color):
    """Create a vertical gradient background."""
    img = Image.new("RGB", (width, height), top_color)
    draw = ImageDraw.Draw(img)
    for y in range(height):
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * y / height)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * y / height)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return img


def extract_hook(post_text, max_chars=140):
    """Pull the hook (first compelling line) from the post."""
    lines = [line.strip() for line in post_text.strip().split("\n") if line.strip()]
    # Skip hashtag-only or very short lines at start
    for line in lines:
        if line.startswith("#"):
            continue
        if len(line) < 15:
            continue
        return line[:max_chars] + ("..." if len(line) > max_chars else "")
    return lines[0][:max_chars] if lines else "New post"


def generate_card(post_text, output_path="post_card.png"):
    """Generate a Canva-style quote card from post text."""
    import random

    template = random.choice(TEMPLATES)
    width, height = 1200, 1200  # Square for LinkedIn

    # Background gradient
    img = make_gradient(width, height, template["bg_top"], template["bg_bottom"])
    draw = ImageDraw.Draw(img)

    # Accent bar (top-left)
    draw.rectangle([(80, 80), (200, 90)], fill=template["accent"])

    # Hook text
    hook = extract_hook(post_text)
    font_main = find_font(64, bold=True)

    # Wrap text to fit width
    wrapped = textwrap.fill(hook, width=24)
    lines = wrapped.split("\n")

    # Vertically center the text block
    line_height = 80
    total_text_height = len(lines) * line_height
    y_start = (height - total_text_height) // 2 - 50

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font_main)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        y = y_start + i * line_height
        draw.text((x, y), line, fill=template["text_color"], font=font_main)

    # Footer branding
    font_footer = find_font(32, bold=True)
    font_handle = find_font(26, bold=False)

    footer_text = "MARIUM SAJJAD"
    handle_text = "Full-Stack Dev · Builder · Karachi"

    bbox = draw.textbbox((0, 0), footer_text, font=font_footer)
    fw = bbox[2] - bbox[0]
    draw.text(((width - fw) // 2, height - 160), footer_text,
              fill=template["accent"], font=font_footer)

    bbox = draw.textbbox((0, 0), handle_text, font=font_handle)
    hw = bbox[2] - bbox[0]
    draw.text(((width - hw) // 2, height - 110), handle_text,
              fill=template["text_color"], font=font_handle)

    # Bottom accent bar
    draw.rectangle([(80, height - 90), (200, height - 80)], fill=template["accent"])

    img.save(output_path, "PNG", optimize=True)
    return output_path
