import config
import sheets
from datetime import datetime, timedelta


def run():
    print("\n=== UNFOLLOWER: Removing non-followers ===\n")

    cl = config.get_client()
    my_id = cl.user_id

    # Get who follows us and who we follow
    print("  Fetching following list...")
    following = cl.user_following(my_id, amount=0)  # 0 = all
    print(f"  Following {len(following)} accounts")

    print("  Fetching followers list...")
    followers = cl.user_followers(my_id, amount=0)
    print(f"  Have {len(followers)} followers")

    follower_ids = set(followers.keys())

    # Get followed records from sheet
    followed_records = sheets.read_tab("Followed")
    cutoff = datetime.now() - timedelta(hours=72)
    unfollowed = 0

    for record in followed_records:
        if unfollowed >= config.MAX_UNFOLLOWS_PER_DAY:
            print(f"\n  Hit daily unfollow limit ({config.MAX_UNFOLLOWS_PER_DAY})")
            break

        user_id = str(record.get("user_id", ""))
        handle = record.get("handle", "")
        date_str = record.get("date_followed", "")
        status = record.get("followed_back", "")

        if status != "pending":
            continue

        # Check if 72h have passed
        try:
            followed_date = datetime.strptime(date_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            continue

        if followed_date > cutoff:
            continue

        uid_int = int(user_id)

        # Check if they followed back
        if uid_int in follower_ids:
            print(f"  @{handle} — followed back!")
            sheets.update_cell_by_match("Followed", "user_id", user_id, "followed_back", "yes")
        else:
            # Unfollow
            try:
                cl.user_unfollow(uid_int)
                print(f"  @{handle} — unfollowed (didn't follow back)")
                sheets.update_cell_by_match("Followed", "user_id", user_id, "followed_back", "no")
                unfollowed += 1
                config.random_delay(config.UNFOLLOW_DELAY)
            except Exception as e:
                print(f"  @{handle} — error unfollowing: {e}")

    print(f"\n  Done — unfollowed {unfollowed} non-followers")


if __name__ == "__main__":
    run()
