import time
import random
from datetime import datetime
import config
import sheets


def follow_user(target_user_id):
    """Follow a user."""
    my_id = config.get_my_user_id()
    return config.api_post(f"users/{my_id}/following", {"target_user_id": target_user_id})


def run():
    print("\n=== FOLLOWER: Following warmed prospects ===\n")

    prospects = sheets.read_tab("Prospects")
    already_followed = sheets.get_existing_followed_ids()

    warmed = [
        p for p in prospects
        if p.get("status") == "warmed" and str(p.get("user_id")) not in already_followed
    ]

    if not warmed:
        print("  No warmed prospects to follow")
        return

    batch = warmed[:config.MAX_FOLLOWS_PER_DAY]
    print(f"  Following {len(batch)} prospects (max {config.MAX_FOLLOWS_PER_DAY} today)\n")

    followed_rows = []
    today = datetime.now().strftime("%Y-%m-%d")

    for prospect in batch:
        handle = prospect["handle"]
        user_id = str(prospect["user_id"])

        try:
            follow_user(user_id)
            print(f"  Followed @{handle}")
            followed_rows.append([handle, user_id, today, "pending"])
            sheets.update_cell_by_match("Prospects", "user_id", user_id, "status", "followed")
        except Exception as e:
            print(f"  Failed to follow @{handle}: {e}")

        delay = random.randint(*config.FOLLOW_DELAY)
        print(f"    Waiting {delay}s...")
        time.sleep(delay)

    if followed_rows:
        sheets.append_rows("Followed", followed_rows)

    print(f"\n  Done. Followed {len(followed_rows)} accounts")


if __name__ == "__main__":
    run()
