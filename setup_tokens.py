"""
Run this ONCE on your local machine to get your LinkedIn OAuth tokens.
"""
import webbrowser
from urllib.parse import parse_qs, urlparse

import requests

REDIRECT_URI = "http://localhost:8080/callback"

client_id = input("Paste your LinkedIn App Client ID: ").strip()
client_secret = input("Paste your LinkedIn App Client Secret: ").strip()

auth_url = (
    "https://www.linkedin.com/oauth/v2/authorization"
    f"?response_type=code"
    f"&client_id={client_id}"
    f"&redirect_uri={REDIRECT_URI}"
    f"&scope=w_member_social"
)

print("\nOpening LinkedIn in your browser...")
print("1. Click ALLOW on the LinkedIn page")
print("2. You will see a 'can't reach this page' error — THAT IS FINE")
print("3. Copy the FULL URL from the browser address bar and paste it below\n")
webbrowser.open(auth_url)

callback_url = input("Paste the full URL from your browser address bar here: ").strip()

params = parse_qs(urlparse(callback_url).query)
if "code" not in params:
    print("No code found in URL. Make sure you copied the full URL.")
    exit(1)

auth_code = params["code"][0]
print("\nGot the code! Fetching tokens...")

resp = requests.post(
    "https://www.linkedin.com/oauth/v2/accessToken",
    data={
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": client_id,
        "client_secret": client_secret,
    },
    timeout=10,
)
resp.raise_for_status()
tokens = resp.json()
access_token = tokens.get("access_token", "")

# Fetch person ID
person_id = ""
if access_token:
    me_resp = requests.get(
        "https://api.linkedin.com/v2/me",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    if me_resp.ok:
        person_id = me_resp.json().get("id", "")

print("\n========== ADD THESE TO GITHUB SECRETS ==========")
print(f"LINKEDIN_CLIENT_ID      = {client_id}")
print(f"LINKEDIN_CLIENT_SECRET  = {client_secret}")
print(f"LINKEDIN_ACCESS_TOKEN   = {access_token or 'ERROR'}")
print(f"LINKEDIN_REFRESH_TOKEN  = {tokens.get('refresh_token', 'NOT PROVIDED')}")
print(f"LINKEDIN_PERSON_ID      = {person_id or 'ERROR'}")
print("=================================================")
print("\nAlso add:")
print("GEMINI_API_KEY          = your key from aistudio.google.com")
