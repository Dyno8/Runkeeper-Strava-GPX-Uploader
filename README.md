# 🏃‍♂️ Runkeeper → Strava GPX Uploader

A Python tool to upload manually exported **GPX files** (from Runkeeper or any GPS source) to **Strava** via the Strava API.

It provides:

- ✅ **Manual GPX uploads** (no Runkeeper API needed)
- ✅ **Automatic token refresh** (new tokens saved into `.env`)
- ✅ **Deduplication** (avoids uploading the same GPX twice)
- ✅ **Custom titles** (Morning / Afternoon / Evening / Night Run, based on filename timestamp)
- ✅ **Polling** Strava until the activity is ready → prints the final Strava activity link

---

## 📂 Project Structure

```
rk2strava/
│── upload_gpx_v2.py     # Main uploader script
│── get_tokens.py        # Helper to fetch initial tokens
│── exports/             # Folder for your GPX files
│── synced.json          # Tracks already uploaded GPX files
│── .env                 # Stores Strava credentials and tokens
│── .env.example         # Template for .env
│── README.md            # Documentation
```

---

## 📦 Installation

Create a virtual environment (optional but recommended):

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install requests python-dotenv
```

---

## 🔑 OAuth Setup (Step by Step)

### 1. Create a Strava App

- Go to [Strava Developer Settings](https://www.strava.com/settings/api).
- Create an app (e.g. `Runkeeper to Strava`).
- Set **Authorization Callback Domain** = `localhost`.
- Copy your **Client ID** and **Client Secret**.

### 2. Build the Authorization URL

Paste this into your browser (replace `YOUR_CLIENT_ID`):

```
https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost/exchange_token&scope=activity:write,activity:read_all
```

### 3. Authorize the App

- Strava will show: **“Authorize <Your App Name> to connect to Strava”**.
- Click **Authorize**.
- You’ll be redirected to a URL like:

```
http://localhost/exchange_token?state=&code=962d8bbf12cbe1c6fb7d010b9b29f7d04799d2f9&scope=read,activity:write,activity:read_all
```

- Copy the **`code=...`** part.

### 4. Run `get_tokens.py`

Run:

```bash
python get_tokens.py
```

Paste the code when prompted.
The script will:

- Exchange it for an `access_token` and `refresh_token`
- Print them in your terminal
- Save them into `.env`

### 5. Ready to Upload!

Now run:

```bash
python upload_gpx_v2.py
```

---

## ▶️ Usage

1. Put your GPX files in the `exports/` folder.
   Example file name: `2025-09-24-175823.gpx`

   - Format: `YYYY-MM-DD-HHMMSS.gpx`

2. Run the uploader:

```bash
python upload_gpx_v2.py
```

---

## 📝 Features

### 🔄 Token Refresh

- Strava access tokens expire every 6 hours.
- Script automatically refreshes them and updates `.env`.

### 🛑 Deduplication

- Uses GPX filename as `external_id`.
- Keeps a local `synced.json`.
- Re-running the script on the same files will skip them.

### 🏷 Custom Titles

- Based on GPX filename timestamp:

  - 05:00–11:59 → Morning Run
  - 12:00–16:59 → Afternoon Run
  - 17:00–21:59 → Evening Run
  - 22:00–04:59 → Night Run

Example:

- `2025-09-24-075823.gpx` → **Morning Run (2025-09-24)**

### ⏳ Polling

- After uploading, script checks Strava until the activity is processed.
- Prints the final Strava URL.

---

## 📊 Example Logs

### First Upload

```
Uploading 2025-09-24-175823.gpx...
 → Upload Response: {'id': 17029564017, 'external_id': '2025-09-24-175823.gpx', 'status': 'Your activity is still being processed.', 'activity_id': None}
 ⏳ Waiting for Strava to process...
   ...still processing
 ✅ Activity ready: https://www.strava.com/activities/1234567890
```

### Second Upload (duplicate file)

```
Uploading 2025-09-24-175823.gpx...
 ⏭ Skipping 2025-09-24-175823.gpx (already uploaded).
```

---

## ⚠️ Notes

- Strava API limits: **100 uploads per 15 minutes**, **1000 per day**.
- Script waits `15s` between uploads to stay safe.
- Processing time per GPX is usually 5–30 seconds.

---

## ✅ Summary

This script is a lightweight way to move your Runkeeper GPX exports into Strava, with safe deduplication, smart activity naming, and automated token management.

---
