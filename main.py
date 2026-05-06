import os
import random
import smtplib
from email.mime.text import MIMEText
from google import genai


# ============================================================
# YOUR PERSONAL CONTEXT — AI writes posts AS you, not generically
# ============================================================
PERSONAL_CONTEXT = """
I am Marium Sajjad, a self-taught full-stack developer based in Karachi, Pakistan.

What I actually do:
- Built archlaneproperties.com — a luxury real estate platform for Northern Cyprus, using Node.js, Supabase, Firebase, Docker, Resend, and self-hosted n8n
- Built an automated LinkedIn content system using Python, GitHub Actions, and Google Gemini API
- I self-host n8n in Docker for workflow automation
- I work with Supabase + Firebase for backends, Resend for emails, OAuth for auth
- I help small businesses automate the boring parts of their operations

My voice:
- Direct, honest, no corporate fluff
- I share real stories from building, not hypothetical advice
- I'm a student but I ship production code — I lead with that
- I use specific numbers and tools, never vague generalities
- I talk like a builder talking to other builders, not a guru selling a course
"""


# ============================================================
# TOPIC POOLS — tied to YOUR actual work + skills
# ============================================================
TOPICS_BY_TYPE = {
    "build_story": [
        "a specific bug I hit while building Archlane and how I fixed it",
        "the moment I realized self-hosting n8n was better than paying for Zapier",
        "what broke at 2 AM when I was deploying my Docker container",
        "why I chose Supabase over Firebase (or vice versa) for a specific feature",
        "the first time a real user signed up on a site I built",
        "how I automated a task that used to take me 2 hours",
        "a feature I thought would be simple but took 3 days",
    ],
    "hot_take": [
        "why most students waste their time on tutorials instead of building",
        "the truth about 'self-taught' developers vs CS degrees",
        "why I stopped using ChatGPT for code and switched to Claude",
        "what no one tells you about hosting your own n8n instance",
        "the hidden cost of 'free' SaaS tools (and when to self-host)",
        "why pretty UIs are killing real product value",
    ],
    "free_value": [
        "a 5-step n8n workflow that saves 10 hours a week",
        "how to set up Supabase auth in under 30 minutes",
        "the exact prompt I use to generate LinkedIn posts with Gemini",
        "how to dockerize a Node.js app in 15 minutes",
        "3 GitHub Actions every developer should set up today",
        "how to use Resend to send transactional emails for free",
        "the AI tools I actually pay for (and why)",
    ],
    "lesson_learned": [
        "what building Archlane taught me about real estate tech",
        "what I learned shipping my first production app at 21",
        "the mistake I made with my first client (and how I fixed it)",
        "why I stopped chasing perfect code and started shipping",
        "what 24 hours of debugging an API taught me about persistence",
    ],
}


# ============================================================
# POST FRAMEWORKS — proven viral structures
# ============================================================
FRAMEWORKS = {
    "build_story": """
Use this STORY framework:
1. HOOK (1 line): a surprising/specific moment ("I deleted 3 hours of work at 2 AM. Here's what I learned.")
2. CONTEXT (2-3 lines): set the scene briefly
3. THE PROBLEM (2-3 lines): what went wrong, get specific
4. THE FIX (3-4 lines): how I solved it, with the actual technical detail
5. THE LESSON (2 lines): what this means for the reader
6. SOFT CTA (1 line): "What's the worst bug you've debugged at 2 AM?" or similar
""",
    "hot_take": """
Use this CONTRARIAN framework:
1. HOOK (1 line): a bold, controversial statement that flips conventional wisdom
2. THE COMMON BELIEF (1-2 lines): what most people think
3. WHY IT'S WRONG (3-4 lines): your specific reasoning, with examples
4. WHAT TO DO INSTEAD (3-4 lines): the better approach with specifics
5. SOFT CTA (1 line): "Disagree? Tell me why in the comments." or similar
""",
    "free_value": """
Use this TUTORIAL framework:
1. HOOK (1 line): the result/outcome they'll get ("This 5-step n8n workflow saved me 10 hours/week")
2. THE PROBLEM IT SOLVES (1-2 lines): why they should care
3. THE STEPS (5-7 short lines): numbered, actionable, specific tools mentioned
4. THE OUTCOME (1-2 lines): what changes after they do this
5. SOFT CTA (1 line): "Want the full code? DM me 'AUTOMATE'." or similar
""",
    "lesson_learned": """
Use this REFLECTION framework:
1. HOOK (1 line): a moment-in-time statement ("3 months ago I couldn't dockerize an app. Today I run my own n8n instance.")
2. WHERE I STARTED (2-3 lines): the gap/struggle
3. WHAT I DID (3-4 lines): the specific actions I took
4. WHERE I AM NOW (2-3 lines): concrete evidence of progress
5. THE MINDSET SHIFT (2 lines): the meta-lesson
6. SOFT CTA (1 line): "What's one skill you're building right now?" or similar
""",
}


# ============================================================
# CTAs that drive PROFILE clicks (real traffic)
# ============================================================
PROFILE_DRIVERS = [
    "If you're building something with Supabase, Node.js, or n8n — let's connect.",
    "Building automations for your business? My DMs are open.",
    "Follow me — I post 3x a week about real builds (not tutorials).",
    "I document every build I ship. Follow if that's your thing.",
    "If you need a website + backend + automation done in 2 weeks instead of 2 months, DM me 'BUILD'.",
]


def generate_post() -> str:
    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

    # Pick a random post type and topic
    post_type = random.choice(list(TOPICS_BY_TYPE.keys()))
    topic = random.choice(TOPICS_BY_TYPE[post_type])
    framework = FRAMEWORKS[post_type]
    cta = random.choice(PROFILE_DRIVERS)

    prompt = f"""You are writing a LinkedIn post AS this person (first person, never third person):

{PERSONAL_CONTEXT}

TODAY'S POST TYPE: {post_type}
TODAY'S TOPIC: {topic}

{framework}

ADDITIONAL RULES:
- Write in first person ("I", not "Marium" or "she")
- Length: 150-250 words MAX
- One idea per line, lots of line breaks for readability
- Use specific tools/numbers/names — never generic ("I used Supabase auth" not "I used a backend service")
- Sound like a real person typing on their phone, not a marketing robot
- Avoid: "In today's fast-paced world", "Excited to share", "Game-changer", "Synergy", any corporate fluff
- Hook MUST stop the scroll — bold claim, surprising fact, or specific moment

End the post with this exact CTA on its own line:
{cta}

Then add 3 relevant hashtags on the final line.

Output ONLY the post text. No preamble, no explanation, no "Here's your post:".
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text


def email_post(content: str) -> None:
    user = os.environ["GMAIL_USER"].strip()
    pwd = os.environ["GMAIL_APP_PASSWORD"].strip()

    msg = MIMEText(content)
    msg["Subject"] = "Your LinkedIn post for today (copy & paste)"
    msg["From"] = user
    msg["To"] = user

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(user, pwd)
        s.send_message(msg)


if __name__ == "__main__":
    post_content = generate_post()
    print(f"--- Generated Post ---\n{post_content}\n----------------------")
    email_post(post_content)
    print("Email sent successfully.")
