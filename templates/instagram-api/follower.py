import config
import sheets
from datetime import datetime


def run():
    print("\n=== FOLLOWER: Following warmed prospects ===\n")

    prospects = sheets.read_tab("Prospects")
    warmed = [p for p in prospects if p.get("status") == "warmed"]
    already_followed = sheets.get_existing_followed_ids()

    to_follow = [p for p in warmed if str(p["user_id"]) not in already_followed]
    to_follow = to_follow[:config.MAX_FOLLOWS_PER_DAY]

    print(f"  Following {len(to_follow)} warmed prospects (max {config.MAX_FOLLOWS_PER_DAY}/day)\n")

    cl = config.get_client()
    followed = 0
    today = datetime.now().strftime("%Y-%m-%d")
    new_rows = []

    for prospect in to_follow:
        handle = prospect["handle"]
        user_id = str(prospect["user_id"])
        print(f"  @{handle}...", end=" ")

        try:
            cl.user_follow(int(user_id))
            print("followed")
            followed += 1

            new_rows.append([handle, user_id, today, "pending"])
            sheets.update_cell_by_match("Prospects", "user_id", user_id, "status", "followed")
            config.random_delay(config.FOLLOW_DELAY)

        except Exception as e:
            print(f"error: {e}")

    if new_rows:
        sheets.append_rows("Followed", new_rows)

    print(f"\n  Done — followed {followed} accounts")


if __name__ == "__main__":
    run()
