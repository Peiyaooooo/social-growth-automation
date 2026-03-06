import config
import sheets


def run():
    print("\n=== WARMER: Liking prospects' posts ===\n")

    prospects = sheets.read_tab("Prospects")
    new_prospects = [p for p in prospects if p.get("status") == "new"]

    max_today = config.MAX_LIKES_PER_DAY // config.LIKES_PER_PROSPECT
    to_warm = new_prospects[:max_today]

    print(f"  Warming up {len(to_warm)} prospects (max {max_today} today)\n")

    cl = config.get_client()
    likes_sent = 0

    for prospect in to_warm:
        handle = prospect["handle"]
        user_id = str(prospect["user_id"])
        print(f"  @{handle}...")

        try:
            uid = cl.user_id_from_username(handle)
            medias = cl.user_medias(uid, amount=5)

            if not medias:
                print(f"    No posts found, skipping")
                sheets.update_cell_by_match("Prospects", "user_id", user_id, "status", "skipped")
                continue

            liked = 0
            for media in medias[:config.LIKES_PER_PROSPECT]:
                try:
                    cl.media_like(media.id)
                    print(f"    Liked post {media.id}")
                    liked += 1
                    likes_sent += 1
                    config.random_delay(config.LIKE_DELAY)
                except Exception as e:
                    print(f"    Error liking: {e}")
                    break

            if liked > 0:
                sheets.update_cell_by_match("Prospects", "user_id", user_id, "status", "warmed")
            else:
                sheets.update_cell_by_match("Prospects", "user_id", user_id, "status", "skipped")

        except Exception as e:
            print(f"    Error: {e}")
            sheets.update_cell_by_match("Prospects", "user_id", user_id, "status", "skipped")

        if likes_sent >= config.MAX_LIKES_PER_DAY:
            print(f"\n  Hit daily like limit ({config.MAX_LIKES_PER_DAY})")
            break

    print(f"\n  Done — {likes_sent} likes sent across {len(to_warm)} prospects")


if __name__ == "__main__":
    run()
