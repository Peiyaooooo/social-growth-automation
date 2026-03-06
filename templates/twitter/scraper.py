import config
import sheets
from datetime import datetime


def get_user_id(username):
    """Resolve a Twitter handle to a user ID."""
    data = config.api_get(f"users/by/username/{username}")
    return data["data"]["id"]


def fetch_followers(user_id, max_count=2000):
    """Fetch up to max_count recent followers of a user."""
    followers = []
    params = {
        "max_results": 1000,
        "user.fields": "public_metrics,created_at,description",
    }
    next_token = None

    while len(followers) < max_count:
        if next_token:
            params["pagination_token"] = next_token

        data = config.api_get(f"users/{user_id}/followers", params=params)

        if "data" not in data:
            break

        followers.extend(data["data"])

        next_token = data.get("meta", {}).get("next_token")
        if not next_token:
            break

    return followers[:max_count]


def filter_prospect(user):
    """Return True if user passes our prospect filters."""
    metrics = user.get("public_metrics", {})
    followers = metrics.get("followers_count", 0)
    tweets = metrics.get("tweet_count", 0)

    if followers < config.MIN_FOLLOWERS:
        return False
    if followers > config.MAX_FOLLOWERS:
        return False
    if tweets < config.MIN_TWEETS:
        return False
    return True


MIN_UNWARMED_PROSPECTS = 200  # Skip scraping if enough prospects are queued


def run():
    print("\n=== SCRAPER: Fetching competitor followers ===\n")

    existing_ids = sheets.get_existing_prospect_ids()
    unwarmed = sheets.count_by_status("Prospects", "new")
    print(f"  Already have {len(existing_ids)} prospects in sheet ({unwarmed} unwarmed)\n")

    if unwarmed >= MIN_UNWARMED_PROSPECTS:
        print(f"  Skipping scrape — still have {unwarmed} unwarmed prospects queued (min {MIN_UNWARMED_PROSPECTS})")
        return

    new_rows = []
    today = datetime.now().strftime("%Y-%m-%d")

    for handle in config.COMPETITORS:
        print(f"  Scraping @{handle}...")
        try:
            user_id = get_user_id(handle)
            followers = fetch_followers(user_id, config.MAX_FOLLOWERS_PER_COMPETITOR)
            print(f"    Fetched {len(followers)} followers")

            added = 0
            for user in followers:
                uid = user["id"]
                if uid in existing_ids:
                    continue
                if not filter_prospect(user):
                    continue

                metrics = user.get("public_metrics", {})
                new_rows.append([
                    user["username"],
                    uid,
                    metrics.get("followers_count", 0),
                    metrics.get("tweet_count", 0),
                    handle,
                    today,
                    "new",
                ])
                existing_ids.add(uid)
                added += 1

            print(f"    Added {added} new prospects (filtered)")

        except Exception as e:
            print(f"    Error scraping @{handle}: {e}")

    if new_rows:
        sheets.append_rows("Prospects", new_rows)
        print(f"\n  Total new prospects added: {len(new_rows)}")
    else:
        print("\n  No new prospects found")


if __name__ == "__main__":
    run()
