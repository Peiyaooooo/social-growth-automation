"""
Instagram Growth Bot — Scheduler
Leave this running in terminal. It handles scraping, warming, following, and unfollowing on a daily schedule.
"""

import schedule
import time
from datetime import datetime
import config


def is_rest_day():
    return datetime.now().weekday() == config.REST_DAY


def morning_job():
    if is_rest_day():
        print(f"\n[{datetime.now()}] Rest day — skipping morning job")
        return

    print(f"\n[{datetime.now()}] Starting morning job: scrape + warm")
    from scraper import run as scrape_run
    from warmer import run as warm_run

    scrape_run()
    warm_run()


def evening_job():
    if is_rest_day():
        print(f"\n[{datetime.now()}] Rest day — skipping evening job")
        return

    print(f"\n[{datetime.now()}] Starting evening job: follow")
    from follower import run as follow_run

    follow_run()


def unfollow_job():
    if is_rest_day():
        print(f"\n[{datetime.now()}] Rest day — skipping unfollow job")
        return

    print(f"\n[{datetime.now()}] Starting unfollow job")
    from unfollower import run as unfollow_run

    unfollow_run()


def main():
    print("=" * 60)
    print("  INSTAGRAM GROWTH BOT — SCHEDULER")
    print("=" * 60)
    print(f"\n  Schedule:")
    print(f"    {config.SCRAPE_TIME}  — Scrape + Warm")
    print(f"    {config.FOLLOW_TIME} — Follow")
    print(f"    {config.UNFOLLOW_TIME}  — Unfollow (every {config.UNFOLLOW_EVERY_N_DAYS} days)")
    print(f"    Rest day: {'Sun' if config.REST_DAY == 6 else 'Mon Tue Wed Thu Fri Sat Sun'.split()[config.REST_DAY]}")
    print(f"\n  Competitors: {', '.join(config.COMPETITORS)}")
    print(f"  Limits: {config.MAX_FOLLOWS_PER_DAY} follows, {config.MAX_LIKES_PER_DAY} likes, {config.MAX_UNFOLLOWS_PER_DAY} unfollows per day")
    print(f"\n  Waiting for scheduled times...\n")

    schedule.every().day.at(config.SCRAPE_TIME).do(morning_job)
    schedule.every().day.at(config.FOLLOW_TIME).do(evening_job)
    schedule.every(config.UNFOLLOW_EVERY_N_DAYS).days.at(config.UNFOLLOW_TIME).do(unfollow_job)

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
