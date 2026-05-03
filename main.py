import os
import random
import requests
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

    response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
    return response.text


def post_to_linkedin(access_token: str, content: str) -> str:
    person_id = os.environ["LINKEDIN_PERSON_ID"]
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "LinkedIn-Version": "202304",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    payload = {
        "author": f"urn:li:person:{person_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": content},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        },
    }
    resp = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers=headers,
        json=payload,
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json().get("id", "unknown")


def refresh_access_token() -> str:
    resp = requests.post(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data={
            "grant_type": "refresh_token",
            "refresh_token": os.environ["LINKEDIN_REFRESH_TOKEN"],
            "client_id": os.environ["LINKEDIN_CLIENT_ID"],
            "client_secret": os.environ["LINKEDIN_CLIENT_SECRET"],
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


if __name__ == "__main__":
    # Use refresh token if available, otherwise fall back to stored access token
    if os.environ.get("LINKEDIN_REFRESH_TOKEN"):
        access_token = refresh_access_token()
        print("Access token refreshed.")
    else:
        access_token = os.environ["LINKEDIN_ACCESS_TOKEN"]

    post_content = generate_post(NICHE, TOPICS)
    print(f"--- Generated Post ---\n{post_content}\n----------------------")

    post_id = post_to_linkedin(access_token, post_content)
    print(f"Posted successfully. Post ID: {post_id}")
