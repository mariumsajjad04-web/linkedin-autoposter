import os
import random
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from google import genai
from image_generator import generate_card


# ============================================================
# YOUR PERSONAL CONTEXT — honest "learning in public" voice
# ============================================================
PERSONAL_CONTEXT = """
I am Marium Sajjad, a CS student in Karachi, Pakistan, learning full-stack development by building real projects.

What I'm actually working on (the truth):
- Recently contributed to a luxury real estate platform (archlaneproperties.com) — got hands-on with Node.js, Supabase, Firebase, Docker, Resend, and n8n. Still learning each one deeply.
- Built an automated LinkedIn content system from scratch (this very tool) using Python, GitHub Actions, and Google Gemini — debugged it for 24 hours before it worked.
- Self-hosting n8n locally in Docker for the first time. Still figuring out workflows.
- Open to internships, freelance projects, and collabs.

My voice — IMPORTANT:
- "Learning in public" — I share what I'm figuring out, NOT what I'm an expert at
- I ask more questions than I make claims
- I use phrases like "I just learned...", "Currently stuck on...", "Anyone know why...", "Today I figured out..."
- I admit when something is hard or when I'm a beginner
- I never claim to be a senior dev or use phrases like "Pro tip:" or "Here's my framework"
- I sound like a curious student-builder, not a guru
- Authentic > impressive
"""


# ============================================================
# TRAFFIC-DRIVING POST TYPES — calibrated for engagement
# ============================================================
TOPICS_BY_TYPE = {
    # Build stories — moments from learning, NOT expert wins
    "build_story": [
        "the moment I realized my Docker container wouldn't start because of a typo",
        "spending 24 hours debugging a LinkedIn API and what I finally found",
        "the weirdest bug I hit while learning Supabase auth",
        "what surprised me the first time I used n8n",
        "why I almost gave up on automation, and what changed my mind",
        "the first time I deployed something and a real person used it",
        "how a simple Gemini API call broke and what I learned",
    ],
    # Hot takes — bold but defensible (things she has actually noticed)
    "hot_take": [
        "why tutorials are slowing you down as a beginner",
        "the real reason most students never ship a project",
        "why self-hosting n8n beats paying for Zapier (a learner's view)",
        "why I stopped trying to memorize syntax and just build instead",
        "why Pakistani devs are underrated globally",
        "what nobody tells beginners about deploying for the first time",
    ],
    # Free value — tiny tips she's actually figured out
    "free_value": [
        "3 things that helped me FINALLY understand OAuth (as a beginner)",
        "the cheat sheet I made for myself to remember Docker commands",
        "the smallest GitHub Actions workflow that changed how I build",
        "the prompts I use with Gemini when I'm stuck on code",
        "how I set up my first Supabase project (and what tripped me up)",
        "the 4-step routine I use to break down a coding problem",
    ],
    # Lessons learned — reflective, builds personal brand
    "lesson_learned": [
        "what 6 months of building taught me about being a 'student'",
        "what I wish I knew before starting my first real project",
        "the mindset shift that made me start shipping instead of studying",
        "what working on a real client project (Archlane) taught me",
        "what I'd tell my younger self about learning to code",
    ],
}


# ============================================================
# POST FRAMEWORKS — calibrated to actually drive engagement
# ============================================================
FRAMEWORKS = {
    "build_story": """
STORY framework (learning-in-public):
1. HOOK (1 line): a specific moment of struggle/discovery ("I deleted 3 hours of work at 2 AM and learned something I'll never forget.")
2. SCENE (2-3 lines): set up what you were trying to do, briefly
3. THE STRUGGLE (2-3 lines): what was confusing/hard — be specific with tools (Docker, n8n, Supabase, etc.)
4. THE FIGURING OUT (3-4 lines): how you eventually understood — name the resource/AI/dev that helped
5. THE TAKEAWAY (2 lines): what this means for other learners
6. ENGAGEMENT QUESTION (1 line): ASK the community ("Senior devs — would you have done it differently?" or "What was your worst debug session?")
""",
    "hot_take": """
CONTRARIAN framework (humble but bold):
1. HOOK (1 line): a punchy claim that goes against common advice ("Tutorials are slowing you down. Here's what I noticed.")
2. CONTEXT (1-2 lines): "I used to believe X..." — show you held the wrong belief
3. WHY YOU CHANGED (3-4 lines): the specific experience that shifted your view
4. WHAT WORKS BETTER (3-4 lines): what you do now instead — concrete and specific
5. ENGAGEMENT QUESTION (1 line): "Am I missing something here? Tell me where I'm wrong."
""",
    "free_value": """
GUIDE framework (humble, useful):
1. HOOK (1 line): "I just figured out X" or "Took me 3 days to learn this. Sharing so you skip the pain."
2. THE PROBLEM (1-2 lines): what most beginners get stuck on (be specific)
3. THE STEPS (4-6 short lines, numbered): exact steps with tool names
4. THE OUTCOME (1-2 lines): what changes after this
5. ENGAGEMENT QUESTION (1 line): "What else should beginners know about [topic]?"
""",
    "lesson_learned": """
REFLECTION framework:
1. HOOK (1 line): a time-anchored moment ("3 months ago I couldn't write a deploy script. Today I run my own n8n in Docker.")
2. WHERE I WAS (2-3 lines): the struggle/gap, honest
3. WHAT CHANGED (3-4 lines): the specific actions — not vague advice, concrete moves
4. WHERE I AM NOW (2-3 lines): evidence of progress
5. THE INSIGHT (2 lines): the deeper realization
6. ENGAGEMENT QUESTION (1 line): "What skill are you building right now?"
""",
}


# ============================================================
# CTAs — engagement-first, traffic-focused
# ============================================================
COMMENT_DRIVERS = [
    "Curious — what would you have done differently?",
    "Senior devs in my network — am I overthinking this?",
    "Drop a 🛠 if you've been here too.",
    "What's the hardest thing you debugged this week?",
    "Anyone else learning this right now? Let's connect.",
    "Tell me where I'm wrong in the comments.",
    "What was YOUR breakthrough moment?",
    "Comment 'BUILD' and I'll DM you what I'm using.",
]


# ============================================================
# GEMINI POST GENERATION
# ============================================================
def generate_post():
    """Returns (post_text, post_type) — needed for image selection."""
    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

    post_type = random.choice(list(TOPICS_BY_TYPE.keys()))
    topic = random.choice(TOPICS_BY_TYPE[post_type])
    framework = FRAMEWORKS[post_type]
    cta = random.choice(COMMENT_DRIVERS)

    prompt = f"""You write LinkedIn posts AS this person (first person):

{PERSONAL_CONTEXT}

POST TYPE: {post_type}
TOPIC: {topic}

{framework}

CRITICAL RULES:
- Length: 130-220 words MAX
- First person ("I", "me", "my") — NEVER "Marium" or third person
- One idea per line, lots of line breaks (LinkedIn reads vertical)
- Specific tools/numbers/names (Supabase, Docker, n8n, Gemini) — never vague
- NO corporate fluff: ban these phrases — "In today's fast-paced world", "Excited to share", "game-changer", "synergy", "leverage", "pro tip"
- Sound like a curious learner, NOT a thought-leader
- Honest about being a learner — phrases like "still figuring out", "just learned", "I'm new to this" are GOOD
- Hook must stop the scroll: specific moment, surprising fact, or honest struggle
- Avoid emojis at the start. Optional in middle/end (1-2 max).

End with this exact engagement question on its own line:
{cta}

Then 3 hashtags on the final line (relevant to the topic, lowercase or PascalCase).

Output ONLY the post text. No preamble.
"""

    models_to_try = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash"]
    last_error = None
    for model in models_to_try:
        for attempt in range(3):
            try:
                response = client.models.generate_content(model=model, contents=prompt)
                return response.text, post_type
            except Exception as e:
                last_error = e
                err = str(e)
                if "503" in err or "UNAVAILABLE" in err or "429" in err:
                    wait = 2 ** attempt
                    print(f"Model {model} attempt {attempt + 1} failed. Retrying in {wait}s...")
                    time.sleep(wait)
                    continue
                print(f"Model {model} hard-failed: {err[:80]}. Trying next model.")
                break
    raise RuntimeError(f"All Gemini models failed. Last: {last_error}")


# ============================================================
# FIRST COMMENT GENERATOR — LinkedIn growth hack
# ============================================================
def generate_first_comment(post_text, post_type):
    """Generate a follow-up comment to post on your own post within 60 seconds.
    This signal triples reach according to LinkedIn algo behavior.
    """
    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

    prompt = f"""You just wrote this LinkedIn post AS Marium Sajjad (CS student, learning in public):

---
{post_text}
---

Now write a short FIRST COMMENT (3-4 sentences) Marium will post on her own post within 60 seconds.

Purpose: spark conversation, ask a deeper follow-up question, OR share one more honest detail.

Rules:
- 3-4 sentences MAX
- First person, casual tone
- Add ONE specific extra detail not in the original post (an exact tool name, time spent, mistake made)
- End with ONE question that invites replies
- No hashtags
- No emojis at start

Output ONLY the comment text.
"""
    try:
        response = client.models.generate_content(model="gemini-2.5-flash-lite", contents=prompt)
        return response.text.strip()
    except Exception as e:
        print(f"First comment generation failed: {e}")
        return "Curious what other learners would do differently here. Drop your take in the replies."


# ============================================================
# EMAIL DELIVERY
# ============================================================
def email_post(post_text, first_comment, post_type, image_path):
    user = os.environ["GMAIL_USER"].strip()
    pwd = os.environ["GMAIL_APP_PASSWORD"].strip()

    msg = MIMEMultipart()
    msg["Subject"] = f"Your LinkedIn post ({post_type.replace('_', ' ').title()})"
    msg["From"] = user
    msg["To"] = user

    body = (
        "═══════════════════════\n"
        "📋 POST TEXT (copy this)\n"
        "═══════════════════════\n\n"
        f"{post_text}\n\n"
        "═══════════════════════\n"
        "💬 FIRST COMMENT (paste this as YOUR first comment within 60 seconds of posting — triples reach)\n"
        "═══════════════════════\n\n"
        f"{first_comment}\n\n"
        "═══════════════════════\n"
        "🎨 IMAGE\n"
        "═══════════════════════\n\n"
        "Attached: post_card.png — upload this with your post.\n\n"
        "═══════════════════════\n"
        "✅ POSTING CHECKLIST\n"
        "═══════════════════════\n\n"
        "1. LinkedIn → Start a post\n"
        "2. Paste the post text above\n"
        "3. Attach post_card.png\n"
        "4. Post\n"
        "5. Within 60 seconds: paste the FIRST COMMENT as your first comment\n"
        "6. Reply to anyone who comments within 2 hours\n\n"
        "Posting + first comment + replies = 3x more reach than just posting.\n"
    )
    msg.attach(MIMEText(body, "plain", "utf-8"))

    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as f:
            img = MIMEImage(f.read())
            img.add_header("Content-Disposition", "attachment", filename="post_card.png")
            msg.attach(img)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(user, pwd)
        s.send_message(msg)


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    post_text, post_type = generate_post()
    print(f"--- {post_type.upper()} ---\n{post_text}\n")

    first_comment = generate_first_comment(post_text, post_type)
    print(f"--- FIRST COMMENT ---\n{first_comment}\n")

    image_path = None
    try:
        image_path = generate_card(post_text, post_type=post_type)
        print(f"Image generated ({post_type}): {image_path}")
    except Exception as e:
        print(f"Image generation failed: {e}")

    email_post(post_text, first_comment, post_type, image_path)
    print("Email sent successfully.")
