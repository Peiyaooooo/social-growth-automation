# PhantomBuster Configuration for Instagram Engage-Then-Follow Strategy
# Replace YOUR_API_KEY with your PhantomBuster API key (found in Account Settings)

PHANTOMBUSTER_API_KEY = "YOUR_API_KEY"

# --- Competitor Config --- CUSTOMIZE THESE ---
# Google Sheet URL containing competitor profile URLs in the Competitors tab
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/"

# --- Phantom Agent IDs --- FILL AFTER CREATING PHANTOMS ---
# After creating each Phantom in PhantomBuster, copy its agent ID from the URL
PHANTOM_IDS = {
    "post_collector": "YOUR_PHANTOM_1_ID",
    "likers_collector": "YOUR_PHANTOM_2_ID",
    "auto_liker": "YOUR_PHANTOM_3_ID",
    "auto_follow": "YOUR_PHANTOM_4_ID",
    "auto_unfollow": "YOUR_PHANTOM_5_ID",
}

# --- Expected Phantom Configuration ---
# These are the expected settings for each Phantom (used by audit.py)
EXPECTED_CONFIG = {
    "1. Post Collector": {
        "script": "Instagram Profile Post Extractor.js",
        "input_should_contain": "google.com/spreadsheets",
        "launch": "repeatedly",
        "required_fields": [
            "sessionCookie",
            "spreadsheetUrl",
            "numberOfPostsPerProfile",
            "numberOfProfilesPerLaunch",
            "columnName",
        ],
    },
    "2. Likers Collector": {
        "script": "Instagram Photo Likers.js",
        "input_should_contain": "phantombuster.s3.amazonaws.com",
        "launch": "after agent",
        "after_name": "1. Post Collector",
        "required_fields": ["sessionCookie", "spreadsheetUrl", "columnName"],
    },
    "3. Auto Liker": {
        "script": "Instagram Auto Liker.js",
        "input_should_contain": "phantombuster.s3.amazonaws.com",
        "launch": "after agent",
        "after_name": "2. Likers Collector",
        "required_fields": ["sessionCookie", "spreadsheetUrl", "columnName", "action"],
        "field_checks": {
            "numberOfPostsPerProfile": {"max": 12},
            "action": {"expected": "Like"},
        },
    },
    "4. Auto Follow": {
        "script": "Instagram Auto Follow.js",
        "input_should_contain": "phantombuster.s3.amazonaws.com",
        "launch": "repeatedly",
        "required_fields": [
            "sessionCookie",
            "spreadsheetUrl",
            "columnName",
            "action",
            "numberOfProfilesPerLaunch",
        ],
        "field_checks": {
            "numberOfProfilesPerLaunch": {"max": 5},
            "action": {"expected": "Follow"},
        },
    },
    "5. Auto Unfollow": {
        "script": "Instagram Auto Unfollow.js",
        "input_should_contain": "phantombuster.s3.amazonaws.com",
        "launch": "repeatedly",
        "required_fields": [
            "sessionCookie",
            "spreadsheetUrl",
            "action",
            "numberOfProfilesPerLaunch",
        ],
        "field_checks": {
            "numberOfProfilesPerLaunch": {"max": 5},
            "action": {"expected": "Unfollow only if they don't follow you"},
        },
    },
}

# --- Safety Limits ---
MAX_FOLLOWS_PER_DAY = 40
MAX_LIKES_PER_DAY = 150
MAX_UNFOLLOWS_PER_DAY = 30
MIN_DELAY_SECONDS = 90
MAX_FOLLOWING_RATIO = 1.5  # following/follower ratio
HARD_FOLLOW_CAP = 7500
COOKIE_REFRESH_DAYS = 5
REST_DAY = "Sunday"
