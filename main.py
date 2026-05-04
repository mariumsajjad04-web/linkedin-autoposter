import os
import random
import smtplib
from email.mime.text import MIMEText
from google import genai


NICHE = os.environ.get("LINKEDIN_NICHE", "tech and software development")
TOPICS = os.environ.get(
    "LINKEDIN_TOPICS",
    "productivity,career lessons,AI tools,side projects,learning in public,mistakes I made"
).split(",")


def generate_post(niche: str, topics: list[str]) -> str:
    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    topic = random.choice(topics).strip()

    prompt = f"""Write a LinkedIn post about: {topic}
Niche: {niche}

Style:
- Hook in the first line that stops the scroll (bold claim, surprising fact, or relatable struggle)
- One idea per line, short punchy sentences
- Share a personal story or lesson from experience
- End with a question to spark comments
- 150-250 words total
- Max 3 hashtags at the end
- Sound human and direct, not corporate

Output only the post text, nothing else."""

    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
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
    post_content = generate_post(NICHE, TOPICS)
    print(f"--- Generated Post ---\n{post_content}\n----------------------")
    email_post(post_content)
    print("Email sent successfully.")
