import os
import time
import json
import requests
from datetime import datetime
from dotenv import load_dotenv, set_key

# ----------------------------
# Load credentials
# ----------------------------
load_dotenv(dotenv_path=".env")

STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
STRAVA_ACCESS_TOKEN = os.getenv("STRAVA_ACCESS_TOKEN")
STRAVA_REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")

STRAVA_UPLOAD_URL = "https://www.strava.com/api/v3/uploads"
STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"

SYNCED_FILE = "synced.json"
if os.path.exists(SYNCED_FILE):
    with open(SYNCED_FILE, "r") as f:
        SYNCED = set(json.load(f))
else:
    SYNCED = set()


# ----------------------------
# Refresh Strava token + save to .env
# ----------------------------
def refresh_strava_token():
    global STRAVA_ACCESS_TOKEN, STRAVA_REFRESH_TOKEN
    resp = requests.post(
        STRAVA_TOKEN_URL,
        data={
            "client_id": STRAVA_CLIENT_ID,
            "client_secret": STRAVA_CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": STRAVA_REFRESH_TOKEN,
        },
    )
    resp.raise_for_status()
    tokens = resp.json()
    STRAVA_ACCESS_TOKEN = tokens["access_token"]
    STRAVA_REFRESH_TOKEN = tokens["refresh_token"]
    set_key(".env", "STRAVA_ACCESS_TOKEN", STRAVA_ACCESS_TOKEN)
    set_key(".env", "STRAVA_REFRESH_TOKEN", STRAVA_REFRESH_TOKEN)
    print("[Strava] Token refreshed.")
    return STRAVA_ACCESS_TOKEN


# ----------------------------
# Make activity title
# ----------------------------
def make_activity_name(filename):
    """Generate activity title from filename timestamp"""
    base = filename.replace(".gpx", "")
    try:
        date_str, time_str = base.rsplit("-", 1)  # YYYY-MM-DD + HHMMSS
        dt = datetime.strptime(date_str + time_str, "%Y-%m-%d%H%M%S")
        hour = dt.hour
        if 5 <= hour < 12:
            label = "Morning Run"
        elif 12 <= hour < 17:
            label = "Afternoon Run"
        elif 17 <= hour < 22:
            label = "Evening Run"
        else:
            label = "Night Run"
        return f"{label} ({date_str})"
    except Exception:
        return base  # fallback if parsing fails


# ----------------------------
# Upload GPX
# ----------------------------
def upload_gpx(file_path, filename):
    global STRAVA_ACCESS_TOKEN

    external_id = filename
    if external_id in SYNCED:
        print(f" ⏭ Skipping {external_id} (already uploaded).")
        return None

    activity_name = make_activity_name(filename)

    headers = {"Authorization": f"Bearer {STRAVA_ACCESS_TOKEN}"}
    files = {"file": (external_id, open(file_path, "rb"), "application/gpx+xml")}
    data = {
        "data_type": "gpx",
        "name": activity_name,
        "external_id": external_id,
    }

    resp = requests.post(STRAVA_UPLOAD_URL, headers=headers, files=files, data=data)

    if resp.status_code == 401:
        print("[Strava] Access token expired, refreshing...")
        refresh_strava_token()
        headers = {"Authorization": f"Bearer {STRAVA_ACCESS_TOKEN}"}
        files = {"file": (external_id, open(file_path, "rb"), "application/gpx+xml")}
        resp = requests.post(STRAVA_UPLOAD_URL, headers=headers, files=files, data=data)

    resp.raise_for_status()
    result = resp.json()

    if not result.get("error"):
        SYNCED.add(external_id)
        with open(SYNCED_FILE, "w") as f:
            json.dump(list(SYNCED), f, indent=2)

    return result


# ----------------------------
# Poll Strava for upload status
# ----------------------------
def check_upload_status(upload_id):
    headers = {"Authorization": f"Bearer {STRAVA_ACCESS_TOKEN}"}
    url = f"https://www.strava.com/api/v3/uploads/{upload_id}"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()


# ----------------------------
# MAIN
# ----------------------------
if __name__ == "__main__":
    gpx_folder = "exports"
    for filename in os.listdir(gpx_folder):
        if filename.endswith(".gpx"):
            path = os.path.join(gpx_folder, filename)
            print(f"Uploading {filename}...")
            result = upload_gpx(path, filename)
            if result:
                print(" → Upload Response:", result)
                upload_id = result["id"]

                # Poll until activity is ready
                print(" ⏳ Waiting for Strava to process...")
                for _ in range(12):  # check up to 2 minutes (12 * 10s)
                    time.sleep(10)
                    status = check_upload_status(upload_id)
                    if status.get("activity_id"):
                        activity_url = f"https://www.strava.com/activities/{status['activity_id']}"
                        print(" ✅ Activity ready:", activity_url)
                        break
                    else:
                        print("   ...still processing")
            time.sleep(15)  # avoid hitting rate limits
