import os
import random
import time
from instagrapi import Client
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# --- Instagram Credentials ---
IG_USERNAME = os.getenv("IG_USERNAME", "")
IG_PASSWORD = os.getenv("IG_PASSWORD", "")
SESSION_FILE = os.path.join(os.path.dirname(__file__), "session.json")

# --- Competitor Config ---
COMPETITORS = ["competitor1", "competitor2"]  # Instagram handles without @
MAX_FOLLOWERS_PER_COMPETITOR = 2000

# --- Prospect Filters ---
MIN_FOLLOWERS = 50
MAX_FOLLOWERS = 50000
MIN_POSTS = 5
MIN_UNWARMED_PROSPECTS = 200  # Skip scraping if enough queued

# --- Daily Limits ---
MAX_FOLLOWS_PER_DAY = 20
MAX_LIKES_PER_DAY = 60
MAX_UNFOLLOWS_PER_DAY = 25
LIKES_PER_PROSPECT = 2

# --- Delays (seconds) — randomized ---
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
GOOGLE_SHEET_NAME = "Instagram Growth Tracker"
GOOGLE_CREDS_FILE = os.path.join(os.path.dirname(__file__), "google_creds.json")


def get_client():
    """Get an authenticated Instagram client with session persistence."""
    cl = Client()
    cl.delay_range = [2, 5]  # Built-in delay between requests

    # Try to load existing session
    if os.path.exists(SESSION_FILE):
        try:
            cl.load_settings(SESSION_FILE)
            cl.login(IG_USERNAME, IG_PASSWORD)
            cl.get_timeline_feed()  # Test if session is valid
            print("  Logged in with saved session")
            return cl
        except Exception:
            print("  Saved session expired, logging in fresh...")

    # Fresh login
    cl.login(IG_USERNAME, IG_PASSWORD)
    cl.dump_settings(SESSION_FILE)
    print("  Logged in and saved session")
    return cl


def random_delay(delay_range):
    """Sleep for a random duration within the range."""
    seconds = random.randint(delay_range[0], delay_range[1])
    print(f"    Waiting {seconds}s...")
    time.sleep(seconds)
