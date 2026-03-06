import config
import sheets
from datetime import datetime


def run():
    print("\n=== SCRAPER: Fetching competitor followers ===\n")

    existing_ids = sheets.get_existing_prospect_ids()
    unwarmed = sheets.count_by_status("Prospects", "new")
    print(f"  Already have {len(existing_ids)} prospects in sheet ({unwarmed} unwarmed)\n")

    if unwarmed >= config.MIN_UNWARMED_PROSPECTS:
        print(f"  Skipping scrape — still have {unwarmed} unwarmed prospects queued (min {config.MIN_UNWARMED_PROSPECTS})")
        return

    cl = config.get_client()
    new_rows = []
    today = datetime.now().strftime("%Y-%m-%d")

    for handle in config.COMPETITORS:
        print(f"  Scraping @{handle}...")
        try:
            user_id = cl.user_id_from_username(handle)
            followers = cl.user_followers(user_id, amount=config.MAX_FOLLOWERS_PER_COMPETITOR)
            print(f"    Fetched {len(followers)} followers")

            added = 0
            for uid, user_info in followers.items():
                uid_str = str(uid)
                if uid_str in existing_ids:
                    continue

                # Get full user info for filtering
                try:
                    full_info = cl.user_info(uid)
                except Exception:
                    continue

                follower_count = full_info.follower_count
                post_count = full_info.media_count

                if follower_count < config.MIN_FOLLOWERS:
                    continue
                if follower_count > config.MAX_FOLLOWERS:
                    continue
                if post_count < config.MIN_POSTS:
                    continue

                new_rows.append([
                    full_info.username,
                    uid_str,
                    follower_count,
                    post_count,
                    handle,
                    today,
                    "new",
                ])
                existing_ids.add(uid_str)
                added += 1

                # Rate limit: don't fetch too many full profiles at once
                if added >= 100:
                    break

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
