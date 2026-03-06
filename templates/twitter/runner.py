import schedule
import time
from datetime import datetime
import config
import sheets
import scraper
import warmer
import follower
import unfollower

DAY_COUNT = 0


def is_rest_day():
    return datetime.now().weekday() == config.REST_DAY


def morning_job():
    """9:00 AM — Scrape + Warm up."""
    if is_rest_day():
        print(f"\n[{datetime.now().strftime('%H:%M')}] Rest day — skipping morning job")
        return
    print(f"\n[{datetime.now().strftime('%H:%M')}] Starting morning job...")
    scraper.run()
    warmer.run()
    print(f"[{datetime.now().strftime('%H:%M')}] Morning job complete")


def evening_job():
    """6:00 PM — Follow warmed prospects."""
    if is_rest_day():
        print(f"\n[{datetime.now().strftime('%H:%M')}] Rest day — skipping evening job")
        return
    print(f"\n[{datetime.now().strftime('%H:%M')}] Starting evening job...")
    follower.run()
    print(f"[{datetime.now().strftime('%H:%M')}] Evening job complete")


def unfollow_job():
    """Every N days — Unfollow non-followers."""
    global DAY_COUNT
    DAY_COUNT += 1
    if DAY_COUNT % config.UNFOLLOW_EVERY_N_DAYS != 0:
        return
    if is_rest_day():
        return
    print(f"\n[{datetime.now().strftime('%H:%M')}] Starting unfollow job...")
    unfollower.run()
    print(f"[{datetime.now().strftime('%H:%M')}] Unfollow job complete")


def main():
    print("=" * 50)
    print("  Twitter Engage-Then-Follow Bot")
    print("=" * 50)
    print(f"  Competitors: {', '.join(config.COMPETITORS)}")
    print(f"  Daily limits: {config.MAX_FOLLOWS_PER_DAY} follows, {config.MAX_LIKES_PER_DAY} likes")
    print(f"  Schedule: scrape {config.SCRAPE_TIME}, follow {config.FOLLOW_TIME}")
    print(f"  Rest day: {'Sun' if config.REST_DAY == 6 else config.REST_DAY}")
    print("=" * 50)

    print("\nChecking Google Sheet tabs...")
    sheets.ensure_tabs_exist()

    schedule.every().day.at(config.SCRAPE_TIME).do(morning_job)
    schedule.every().day.at(config.FOLLOW_TIME).do(evening_job)
    schedule.every().day.at(config.UNFOLLOW_TIME).do(unfollow_job)

    print(f"\nBot running. Press Ctrl+C to stop.\n")

    try:
        while True:
            schedule.run_pending()
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n\nBot stopped gracefully.")


if __name__ == "__main__":
    main()
