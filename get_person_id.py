import requests

client_id = input("Paste your LINKEDIN_CLIENT_ID: ").strip()
client_secret = input("Paste your LINKEDIN_CLIENT_SECRET: ").strip()
token = input("Paste your LINKEDIN_ACCESS_TOKEN: ").strip()

resp = requests.post(
    "https://www.linkedin.com/oauth/v2/introspectToken",
    data={
        "client_id": client_id,
        "client_secret": client_secret,
        "token": token,
    },
    timeout=10,
)

data = resp.json()
print("\nFull response:", data)
person_id = data.get("sub", "not found")
print(f"\nYour LINKEDIN_PERSON_ID = {person_id}")
