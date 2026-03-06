import time
import random
import config
import sheets


def get_recent_tweets(user_id, count=5):
    """Get a user's recent tweets."""
    params = {
        "max_results": min(count, 100),
        "tweet.fields": "created_at",
    }
    try:
        data = config.api_get(f"users/{user_id}/tweets", params=params)
        return data.get("data", [])
    except Exception as e:
        print(f"    Could not fetch tweets: {e}")
        return []


def like_tweet(tweet_id):
    """Like a tweet."""
    my_id = config.get_my_user_id()
    return config.api_post(f"users/{my_id}/likes", {"tweet_id": tweet_id})


def run():
    print("\n=== WARMER: Liking prospects' tweets ===\n")

    prospects = sheets.read_tab("Prospects")
    new_prospects = [p for p in prospects if p.get("status") == "new"]

    if not new_prospects:
        print("  No new prospects to warm up")
        return

    max_prospects = config.MAX_LIKES_PER_DAY // config.LIKES_PER_PROSPECT
    batch = new_prospects[:max_prospects]
    print(f"  Warming up {len(batch)} prospects (max {max_prospects} today)\n")

    total_likes = 0

    for prospect in batch:
        handle = prospect["handle"]
        user_id = str(prospect["user_id"])
        print(f"  @{handle}...")

        tweets = get_recent_tweets(user_id)
        if not tweets:
            print(f"    No tweets found, skipping")
            sheets.update_cell_by_match("Prospects", "user_id", user_id, "status", "skipped")
            continue

        tweets_to_like = tweets[:config.LIKES_PER_PROSPECT]
        liked = 0

        for tweet in tweets_to_like:
            try:
                like_tweet(tweet["id"])
                liked += 1
                total_likes += 1
                print(f"    Liked tweet {tweet['id']}")
            except Exception as e:
                print(f"    Failed to like: {e}")

            if total_likes >= config.MAX_LIKES_PER_DAY:
                print(f"\n  Daily like limit reached ({config.MAX_LIKES_PER_DAY})")
                break

            delay = random.randint(*config.LIKE_DELAY)
            print(f"    Waiting {delay}s...")
            time.sleep(delay)

        if liked > 0:
            sheets.update_cell_by_match("Prospects", "user_id", user_id, "status", "warmed")

        if total_likes >= config.MAX_LIKES_PER_DAY:
            break

    print(f"\n  Done. Total likes: {total_likes}")


if __name__ == "__main__":
    run()
