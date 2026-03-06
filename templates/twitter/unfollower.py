import time
import random
from datetime import datetime, timedelta
import config
import sheets


def get_my_follower_ids():
    """Get set of user IDs that follow the authenticated user."""
    my_id = config.get_my_user_id()
    follower_ids = set()
    params = {"max_results": 1000}
    next_token = None

    while True:
        if next_token:
            params["pagination_token"] = next_token

        data = config.api_get(f"users/{my_id}/followers", params=params)

        if "data" in data:
            for user in data["data"]:
                follower_ids.add(user["id"])

        next_token = data.get("meta", {}).get("next_token")
        if not next_token:
            break

    return follower_ids


def unfollow_user(target_user_id):
    """Unfollow a user."""
    my_id = config.get_my_user_id()
    return config.api_delete(f"users/{my_id}/following/{target_user_id}")


def run():
    print("\n=== UNFOLLOWER: Cleaning up non-followers ===\n")

    followed = sheets.read_tab("Followed")
    pending = [f for f in followed if f.get("followed_back") == "pending"]

    if not pending:
        print("  No pending follows to check")
        return

    cutoff = datetime.now() - timedelta(hours=72)
    old_enough = []
    for f in pending:
        try:
            follow_date = datetime.strptime(str(f["date_followed"]), "%Y-%m-%d")
            if follow_date <= cutoff:
                old_enough.append(f)
        except (ValueError, KeyError):
            continue

    if not old_enough:
        print("  No follows old enough to check (need 72h)")
        return

    print(f"  Checking {len(old_enough)} follows older than 72h\n")
    print("  Fetching your followers list...")
    my_followers = get_my_follower_ids()
    print(f"  You have {len(my_followers)} followers\n")

    unfollowed = 0

    for f in old_enough:
        user_id = str(f["user_id"])
        handle = f["handle"]

        if user_id in my_followers:
            print(f"  @{handle} followed back!")
            sheets.update_cell_by_match("Followed", "user_id", user_id, "followed_back", "yes")
        else:
            if unfollowed >= config.MAX_UNFOLLOWS_PER_DAY:
                print(f"\n  Daily unfollow limit reached ({config.MAX_UNFOLLOWS_PER_DAY})")
                break

            try:
                unfollow_user(user_id)
                print(f"  Unfollowed @{handle} (no follow-back)")
                sheets.update_cell_by_match("Followed", "user_id", user_id, "followed_back", "no")
                unfollowed += 1
            except Exception as e:
                print(f"  Failed to unfollow @{handle}: {e}")

            delay = random.randint(*config.UNFOLLOW_DELAY)
            time.sleep(delay)

    print(f"\n  Done. Unfollowed {unfollowed} non-followers")


if __name__ == "__main__":
    run()
