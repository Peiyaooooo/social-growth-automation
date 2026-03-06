"""
Quick daily check — shows the latest output from each Phantom.
Run this to see if today's automation ran successfully.
"""

import json
import urllib.request
import datetime
from config import PHANTOMBUSTER_API_KEY, PHANTOM_IDS

NAMES = {
    "post_collector": "1. Post Collector",
    "likers_collector": "2. Likers Collector",
    "auto_liker": "3. Auto Liker",
    "auto_follow": "4. Auto Follow",
    "auto_unfollow": "5. Auto Unfollow",
}


def run():
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    for key, agent_id in PHANTOM_IDS.items():
        name = NAMES.get(key, key)
        print(f"{'=' * 60}")
        print(f"  {name}")
        print(f"{'=' * 60}")

        if agent_id.startswith("YOUR_"):
            print(f"  Not configured yet — set PHANTOM_IDS in config.py")
            print()
            continue

        try:
            req = urllib.request.Request(
                f"https://api.phantombuster.com/api/v2/agents/fetch-output?id={agent_id}",
                headers={"X-Phantombuster-Key": PHANTOMBUSTER_API_KEY},
            )
            with urllib.request.urlopen(req) as resp:
                raw = resp.read().decode("utf-8", errors="replace")

            d = json.loads(
                raw.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
            )

            status = d.get("status", "unknown")
            output = (
                d.get("output", "")
                .replace("\\n", "\n")
                .replace("\\r", "")
                .replace("\\t", "\t")
            )

            print(f"  Status: {status}")

            lines = [l for l in output.split("\n") if l.strip()]
            for l in lines[-15:]:
                print(f"  {l}")

        except Exception as e:
            print(f"  Error fetching: {e}")

        print()


if __name__ == "__main__":
    run()
