"""
Generate distinct, modern image templates for each LinkedIn post type.
4 templates: code_terminal, quote_bold, checklist, split_reflection.
Pure PIL — works on GitHub Actions, zero external dependencies.
"""
import os
import random
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter


# ============================================================
# COLOR PALETTES — designer-grade, modern
# ============================================================
PALETTES = [
    {
        "name": "midnight",
        "bg": (13, 17, 23),         # GitHub dark
        "bg_alt": (22, 27, 34),
        "accent": (88, 166, 255),   # Blue
        "accent2": (255, 123, 114), # Coral
        "text": (240, 246, 252),
        "muted": (139, 148, 158),
    },
    {
        "name": "neon_purple",
        "bg": (15, 10, 30),
        "bg_alt": (30, 20, 60),
        "accent": (192, 132, 252),  # Purple
        "accent2": (244, 114, 182), # Pink
        "text": (250, 250, 255),
        "muted": (160, 150, 180),
    },
    {
        "name": "emerald",
        "bg": (5, 15, 25),
        "bg_alt": (10, 30, 40),
        "accent": (52, 211, 153),   # Emerald
        "accent2": (251, 191, 36),  # Amber
        "text": (240, 255, 250),
        "muted": (130, 160, 150),
    },
    {
        "name": "sunset",
        "bg": (25, 10, 30),
        "bg_alt": (60, 20, 50),
        "accent": (251, 146, 60),   # Orange
        "accent2": (236, 72, 153),  # Pink
        "text": (255, 250, 240),
        "muted": (180, 140, 160),
    },
]


# ============================================================
# FONT DISCOVERY
# ============================================================
def find_font(size, weight="regular"):
    """Find a usable system font, preferring modern variants."""
    if weight == "bold":
        paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf",
            "C:\\Windows\\Fonts\\seguibl.ttf",
        ]
    elif weight == "mono":
        paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
            "C:\\Windows\\Fonts\\consolab.ttf",
            "C:\\Windows\\Fonts\\consola.ttf",
        ]
    else:
        paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "C:\\Windows\\Fonts\\arial.ttf",
            "C:\\Windows\\Fonts\\segoeui.ttf",
        ]
    for path in paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


# ============================================================
# HELPERS
# ============================================================
def make_gradient(width, height, top, bottom):
    img = Image.new("RGB", (width, height), top)
    draw = ImageDraw.Draw(img)
    for y in range(height):
        r = int(top[0] + (bottom[0] - top[0]) * y / height)
        g = int(top[1] + (bottom[1] - top[1]) * y / height)
        b = int(top[2] + (bottom[2] - top[2]) * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return img


def add_glow_dot(draw, x, y, radius, color):
    """Soft glowing accent dot."""
    for r in range(radius * 3, 0, -1):
        alpha = int(255 * (1 - r / (radius * 3)) ** 2)
        c = (*color, alpha) if len(color) == 3 else color
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color)


def draw_text_centered(draw, y, text, font, color, width):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((width - tw) // 2, y), text, fill=color, font=font)


def extract_hook(post_text, max_chars=120):
    lines = [l.strip() for l in post_text.strip().split("\n") if l.strip()]
    for line in lines:
        if line.startswith("#"):
            continue
        if len(line) < 15:
            continue
        return line[:max_chars] + ("..." if len(line) > max_chars else "")
    return lines[0][:max_chars] if lines else "New post"


def add_branding(draw, width, height, palette):
    """Consistent footer branding across all templates."""
    f_name = find_font(28, "bold")
    f_handle = find_font(22, "regular")

    # Bottom accent line
    draw.rectangle([(80, height - 100), (130, height - 96)], fill=palette["accent"])

    # Name + handle
    draw.text((80, height - 80), "MARIUM SAJJAD",
              fill=palette["text"], font=f_name)
    draw.text((80, height - 45), "Building stuff · Karachi 🇵🇰",
              fill=palette["muted"], font=f_handle)

    # Top-right accent
    draw.rectangle([(width - 130, 80), (width - 80, 84)], fill=palette["accent2"])


# ============================================================
# TEMPLATE 1: CODE TERMINAL (for build stories)
# ============================================================
def template_code_terminal(post_text, palette):
    W, H = 1200, 1200
    img = make_gradient(W, H, palette["bg"], palette["bg_alt"])
    draw = ImageDraw.Draw(img)

    # Terminal window mockup
    term_x1, term_y1 = 100, 250
    term_x2, term_y2 = W - 100, H - 250

    # Window shadow
    shadow = Image.new("RGBA", (term_x2 - term_x1 + 40, term_y2 - term_y1 + 40), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle([0, 0, term_x2 - term_x1 + 40, term_y2 - term_y1 + 40],
                                   radius=20, fill=(0, 0, 0, 100))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=15))
    img.paste(shadow, (term_x1 - 20, term_y1 - 10), shadow)

    # Window body
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([term_x1, term_y1, term_x2, term_y2],
                            radius=16, fill=palette["bg_alt"])

    # Title bar
    draw.rounded_rectangle([term_x1, term_y1, term_x2, term_y1 + 50],
                            radius=16, fill=(palette["bg"][0] + 10, palette["bg"][1] + 10, palette["bg"][2] + 10))
    # Window controls (dots)
    draw.ellipse([term_x1 + 25, term_y1 + 18, term_x1 + 45, term_y1 + 38], fill=(255, 95, 86))
    draw.ellipse([term_x1 + 55, term_y1 + 18, term_x1 + 75, term_y1 + 38], fill=(255, 189, 46))
    draw.ellipse([term_x1 + 85, term_y1 + 18, term_x1 + 105, term_y1 + 38], fill=(39, 201, 63))

    # Title text
    f_title = find_font(18, "mono")
    draw.text((term_x1 + 130, term_y1 + 22), "marium@karachi:~/builds$",
              fill=palette["muted"], font=f_title)

    # Code content
    hook = extract_hook(post_text, 110)
    f_code = find_font(36, "mono")
    f_prompt = find_font(38, "mono")

    # Wrap hook
    wrapped = textwrap.fill(hook, width=28)
    lines = wrapped.split("\n")

    code_y = term_y1 + 110
    # Prompt symbol
    draw.text((term_x1 + 40, code_y), "$", fill=palette["accent"], font=f_prompt)
    # Hook text
    for i, line in enumerate(lines):
        draw.text((term_x1 + 90, code_y + i * 55), line,
                  fill=palette["text"], font=f_code)

    # Cursor blink
    cursor_y = code_y + len(lines) * 55
    draw.rectangle([term_x1 + 90, cursor_y + 5, term_x1 + 110, cursor_y + 40],
                   fill=palette["accent"])

    # Top label
    f_label = find_font(24, "bold")
    draw.text((100, 120), "BUILD LOG", fill=palette["accent2"], font=f_label)

    add_branding(draw, W, H, palette)
    return img


# ============================================================
# TEMPLATE 2: BOLD QUOTE (for hot takes)
# ============================================================
def template_bold_quote(post_text, palette):
    W, H = 1200, 1200
    img = make_gradient(W, H, palette["bg"], palette["bg_alt"])
    draw = ImageDraw.Draw(img)

    # Large quote mark in background
    f_quote = find_font(400, "bold")
    draw.text((60, -60), '"', fill=palette["accent"] + (50,) if len(palette["accent"]) == 4 else palette["accent"], font=f_quote)

    # Top label
    f_label = find_font(26, "bold")
    draw.text((100, 200), "HOT TAKE", fill=palette["accent2"], font=f_label)
    draw.rectangle([(100, 240), (180, 244)], fill=palette["accent2"])

    # Main hook
    hook = extract_hook(post_text, 130)
    f_main = find_font(70, "bold")
    wrapped = textwrap.fill(hook, width=20)
    lines = wrapped.split("\n")

    total_h = len(lines) * 85
    y_start = (H - total_h) // 2 - 60
    for i, line in enumerate(lines):
        draw.text((100, y_start + i * 85), line, fill=palette["text"], font=f_main)

    # Bottom accent
    draw.rectangle([(100, H - 230), (W - 100, H - 226)], fill=palette["accent"])

    add_branding(draw, W, H, palette)
    return img


# ============================================================
# TEMPLATE 3: CHECKLIST (for free value posts)
# ============================================================
def extract_numbered_steps(post_text, max_items=5, max_chars=28):
    """Pull numbered list items (1., 2., etc.) from the post body."""
    import re
    items = []
    for line in post_text.split("\n"):
        line = line.strip()
        # Match "1." "1)" "1:" patterns
        m = re.match(r"^(\d+)[\.\):\-]\s*(.+)$", line)
        if m:
            text = m.group(2).strip()
            # Strip leading quotes/markdown
            text = text.strip('"\'*`').strip()
            # Take just the first clause (before period or comma)
            text = re.split(r"[\.,:]", text, maxsplit=1)[0]
            text = text[:max_chars] + ("..." if len(text) > max_chars else "")
            items.append(text)
            if len(items) >= max_items:
                break
    return items


def template_checklist(post_text, palette):
    W, H = 1200, 1200
    img = make_gradient(W, H, palette["bg"], palette["bg_alt"])
    draw = ImageDraw.Draw(img)

    # Top label
    f_label = find_font(26, "bold")
    draw.text((100, 100), "FREE GUIDE", fill=palette["accent2"], font=f_label)
    draw.rectangle([(100, 140), (200, 144)], fill=palette["accent2"])

    # Title — wrap nicely, smaller font, no truncation
    hook = extract_hook(post_text, 90)
    f_title = find_font(46, "bold")
    wrapped = textwrap.fill(hook, width=26)
    lines = wrapped.split("\n")[:3]  # Cap at 3 lines visually

    title_y = 180
    for i, line in enumerate(lines):
        draw.text((100, title_y + i * 58), line, fill=palette["text"], font=f_title)

    # Real numbered items from the post (with fallback)
    steps = extract_numbered_steps(post_text, max_items=4, max_chars=32)
    if not steps:
        steps = ["See post for details", "Step-by-step inside", "Real example included",
                 "Quick to apply"]

    f_check = find_font(28, "regular")
    check_y = title_y + len(lines) * 58 + 60
    for i, item in enumerate(steps):
        y = check_y + i * 70
        # Checkbox
        draw.rounded_rectangle([100, y, 145, y + 45], radius=8,
                                outline=palette["accent"], width=3)
        # Check mark
        draw.line([(112, y + 22), (122, y + 32), (138, y + 14)],
                  fill=palette["accent"], width=4)
        # Text — truncated to fit width
        draw.text((170, y + 7), item, fill=palette["muted"], font=f_check)

    # CTA badge — fixed width to prevent overflow
    f_badge = find_font(24, "bold")
    cta = "Follow for more"
    bbox = draw.textbbox((0, 0), cta, font=f_badge)
    badge_w = bbox[2] - bbox[0] + 60
    badge_y_top = H - 200
    badge_y_bot = H - 145
    draw.rounded_rectangle([(100, badge_y_top), (100 + badge_w, badge_y_bot)],
                            radius=28, fill=palette["accent"])
    draw.text((130, badge_y_top + 13), cta, fill=palette["bg"], font=f_badge)

    add_branding(draw, W, H, palette)
    return img


# ============================================================
# TEMPLATE 4: SPLIT REFLECTION (for lessons)
# ============================================================
def template_split_reflection(post_text, palette):
    W, H = 1200, 1200
    img = make_gradient(W, H, palette["bg"], palette["bg_alt"])
    draw = ImageDraw.Draw(img)

    # Top label
    f_label = find_font(26, "bold")
    draw.text((100, 120), "WHAT I LEARNED", fill=palette["accent2"], font=f_label)
    draw.rectangle([(100, 160), (250, 164)], fill=palette["accent2"])

    # Big numeric accent
    f_huge = find_font(280, "bold")
    draw.text((W - 380, 200), "01", fill=palette["accent"] + (30,) if False else palette["accent"], font=f_huge)

    # Main hook
    hook = extract_hook(post_text, 130)
    f_main = find_font(58, "bold")
    wrapped = textwrap.fill(hook, width=22)
    lines = wrapped.split("\n")

    y_start = 280
    for i, line in enumerate(lines):
        draw.text((100, y_start + i * 75), line, fill=palette["text"], font=f_main)

    # Divider
    div_y = y_start + len(lines) * 75 + 60
    draw.line([(100, div_y), (W - 100, div_y)], fill=palette["accent"], width=3)

    # Sub-message
    f_sub = find_font(32, "regular")
    sub_lines = ["Building in public.", "Sharing what works (and what doesn't)."]
    for i, sl in enumerate(sub_lines):
        draw.text((100, div_y + 40 + i * 50), sl, fill=palette["muted"], font=f_sub)

    add_branding(draw, W, H, palette)
    return img


# ============================================================
# DISPATCHER
# ============================================================
TEMPLATE_MAP = {
    "build_story": template_code_terminal,
    "hot_take": template_bold_quote,
    "free_value": template_checklist,
    "lesson_learned": template_split_reflection,
}


def generate_card(post_text, post_type="build_story", output_path="post_card.png"):
    template_fn = TEMPLATE_MAP.get(post_type, template_code_terminal)
    palette = random.choice(PALETTES)
    img = template_fn(post_text, palette)
    img.save(output_path, "PNG", optimize=True)
    return output_path
