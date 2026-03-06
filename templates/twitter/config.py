import os
import time
import hashlib
import hmac
import base64
import urllib.parse
import uuid
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# --- Twitter API Credentials ---
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")
API_KEY = os.getenv("TWITTER_API_KEY", "")
API_SECRET = os.getenv("TWITTER_API_SECRET", "")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "")
ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")

# --- Competitor Config --- CUSTOMIZE THESE ---
COMPETITORS = ["competitor1", "competitor2"]
MAX_FOLLOWERS_PER_COMPETITOR = 2000

# --- Prospect Filters ---
MIN_FOLLOWERS = 50
MAX_FOLLOWERS = 50000
MIN_TWEETS = 10

# --- Daily Limits (Week 1) --- ADJUST WEEKLY ---
MAX_FOLLOWS_PER_DAY = 20
MAX_LIKES_PER_DAY = 60
MAX_UNFOLLOWS_PER_DAY = 25
LIKES_PER_PROSPECT = 2

# --- Delays (seconds) — randomized between min, max ---
LIKE_DELAY = (60, 90)
FOLLOW_DELAY = (90, 120)
UNFOLLOW_DELAY = (90, 120)

# --- Schedule ---
SCRAPE_TIME = "09:00"
WARM_TIME = "09:15"
FOLLOW_TIME = "18:00"
UNFOLLOW_TIME = "10:00"
UNFOLLOW_EVERY_N_DAYS = 3
REST_DAY = 6  # Sunday (0=Monday, 6=Sunday)

# --- Google Sheets ---
GOOGLE_SHEET_NAME = "Twitter Growth Tracker"
GOOGLE_CREDS_FILE = os.path.join(os.path.dirname(__file__), "google_creds.json")

# --- API Base URL ---
BASE_URL = "https://api.x.com/2"


def bearer_headers():
    """Headers for read-only endpoints (GET requests)."""
    return {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json",
    }


def _percent_encode(s):
    return urllib.parse.quote(str(s), safe="")


def oauth1_headers(method, url, params=None):
    """Build OAuth 1.0a headers for write endpoints (POST/DELETE)."""
    if params is None:
        params = {}

    oauth_params = {
        "oauth_consumer_key": API_KEY,
        "oauth_nonce": uuid.uuid4().hex,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": ACCESS_TOKEN,
        "oauth_version": "1.0",
    }

    all_params = {**oauth_params, **params}
    sorted_params = "&".join(
        f"{_percent_encode(k)}={_percent_encode(v)}"
        for k, v in sorted(all_params.items())
    )

    base_string = f"{method.upper()}&{_percent_encode(url)}&{_percent_encode(sorted_params)}"
    signing_key = f"{_percent_encode(API_SECRET)}&{_percent_encode(ACCESS_TOKEN_SECRET)}"

    signature = base64.b64encode(
        hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
    ).decode()

    oauth_params["oauth_signature"] = signature

    auth_header = "OAuth " + ", ".join(
        f'{_percent_encode(k)}="{_percent_encode(v)}"'
        for k, v in sorted(oauth_params.items())
    )

    return {
        "Authorization": auth_header,
        "Content-Type": "application/json",
    }


def api_get(endpoint, params=None):
    """Make authenticated GET request to Twitter API v2 using OAuth 1.0a."""
    url = f"{BASE_URL}/{endpoint}"
    headers = oauth1_headers("GET", url, params or {})
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code == 429:
        reset = int(resp.headers.get("x-rate-limit-reset", time.time() + 60))
        wait = max(reset - int(time.time()), 5)
        print(f"  Rate limited. Waiting {wait}s...")
        time.sleep(wait)
        headers = oauth1_headers("GET", url, params or {})
        resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()


def api_post(endpoint, json_body=None):
    """Make authenticated POST request to Twitter API v2."""
    url = f"{BASE_URL}/{endpoint}"
    headers = oauth1_headers("POST", url)
    resp = requests.post(url, headers=headers, json=json_body)
    if resp.status_code == 429:
        reset = int(resp.headers.get("x-rate-limit-reset", time.time() + 60))
        wait = max(reset - int(time.time()), 5)
        print(f"  Rate limited. Waiting {wait}s...")
        time.sleep(wait)
        resp = requests.post(url, headers=headers, json=json_body)
    resp.raise_for_status()
    return resp.json()


def api_delete(endpoint):
    """Make authenticated DELETE request to Twitter API v2."""
    url = f"{BASE_URL}/{endpoint}"
    headers = oauth1_headers("DELETE", url)
    resp = requests.delete(url, headers=headers)
    if resp.status_code == 429:
        reset = int(resp.headers.get("x-rate-limit-reset", time.time() + 60))
        wait = max(reset - int(time.time()), 5)
        print(f"  Rate limited. Waiting {wait}s...")
        time.sleep(wait)
        resp = requests.delete(url, headers=headers)
    resp.raise_for_status()
    return resp.json()


def get_my_user_id():
    """Get the authenticated user's ID."""
    data = api_get("users/me")
    return data["data"]["id"]
