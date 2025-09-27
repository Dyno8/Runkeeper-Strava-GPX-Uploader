import os
import requests
from dotenv import load_dotenv, set_key

# ----------------------------
# Load existing .env
# ----------------------------
load_dotenv(dotenv_path=".env")

STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")

if not STRAVA_CLIENT_ID or not STRAVA_CLIENT_SECRET:
    raise ValueError("⚠️ Please set STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET in .env first")

# ----------------------------
# Ask for authorization code
# ----------------------------
auth_code = input("Paste the 'code' you got from Strava redirect URL: ").strip()

# ----------------------------
# Exchange code for tokens
# ----------------------------
resp = requests.post(
    "https://www.strava.com/oauth/token",
    data={
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "code": auth_code,
        "grant_type": "authorization_code",
    },
)

resp.raise_for_status()
tokens = resp.json()

access_token = tokens["access_token"]
refresh_token = tokens["refresh_token"]
expires_at = tokens["expires_at"]

print("\n✅ Tokens received:")
print("Access Token:", access_token)
print("Refresh Token:", refresh_token)
print("Expires At:", expires_at)

# ----------------------------
# Save to .env
# ----------------------------
set_key(".env", "STRAVA_ACCESS_TOKEN", access_token)
set_key(".env", "STRAVA_REFRESH_TOKEN", refresh_token)

print("\n💾 Saved STRAVA_ACCESS_TOKEN and STRAVA_REFRESH_TOKEN into .env")
