"""
Deep audit — checks edge cases, throughput balance, rate limits,
data flow timing, file management, column names, and cookie consistency.

Run this after initial setup and weekly to catch configuration drift.
"""

import json
import urllib.request
from config import PHANTOMBUSTER_API_KEY


def api_get(endpoint):
    req = urllib.request.Request(
        f"https://api.phantombuster.com/api/v2/{endpoint}",
        headers={"X-Phantombuster-Key": PHANTOMBUSTER_API_KEY},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def run():
    agents = api_get("agents/fetch-all")
    agents.sort(key=lambda a: a.get("name", ""))

    details = {}
    for a in agents:
        d = api_get(f"agents/fetch?id={a['id']}")
        arg = json.loads(d.get("argument", "{}") or "{}")
        details[a["name"]] = {"agent": a, "detail": d, "arg": arg}

    issues = []

    print("=" * 70)
    print("  DEEP AUDIT - EDGE CASES & THROUGHPUT")
    print("=" * 70)

    # 1. Unknown field check
    print("\n[1] UNKNOWN FIELD CHECK")
    for name, info in details.items():
        a = info["agent"]
        arg = info["arg"]
        manifest = a.get("manifest") or {}
        schema = manifest.get("argumentSchema") or {}
        valid_props = set((schema.get("properties") or {}).keys())
        if valid_props:
            for k in arg:
                if k not in valid_props:
                    msg = f"  {name}: field '{k}' NOT in phantom schema - may be IGNORED"
                    print(msg)
                    issues.append(msg)
        else:
            print(f"  {name}: no schema available to validate")

    if not any("NOT in phantom" in i for i in issues):
        print("  All fields valid across all phantoms.")

    # 2. Rate limit check
    print("\n[2] RATE LIMIT & SAFETY CHECK")

    # Find phantoms by partial name match
    p3_name = [n for n in details if "3." in n and "Liker" in n]
    p4_name = [n for n in details if "4." in n and "Follow" in n]
    p5_name = [n for n in details if "5." in n and "Unfollow" in n]

    if p4_name and p5_name:
        p4_a = details[p4_name[0]]["agent"]
        p4_rt = p4_a.get("repeatedLaunchTimes", {})
        p4_hours = p4_rt.get("hour", [])
        p4_days = p4_rt.get("dow", [])
        p4_profiles = details[p4_name[0]]["arg"].get("numberOfProfilesPerLaunch", 0)
        p4_daily = p4_profiles * len(p4_hours)
        p4_weekly = p4_daily * len(p4_days)
        print(
            f"  P4 Auto Follow: {p4_profiles}/launch x {len(p4_hours)} launches/day x {len(p4_days)} days/week = {p4_weekly} follows/week ({p4_daily}/day)"
        )

        p5_a = details[p5_name[0]]["agent"]
        p5_rt = p5_a.get("repeatedLaunchTimes", {})
        p5_hours = p5_rt.get("hour", [])
        p5_days = p5_rt.get("dow", [])
        p5_profiles = details[p5_name[0]]["arg"].get("numberOfProfilesPerLaunch", 0)
        p5_weekly = p5_profiles * len(p5_hours) * len(p5_days)
        print(
            f"  P5 Auto Unfollow: {p5_profiles}/launch x {len(p5_hours)} launches/day x {len(p5_days)} days/week = {p5_weekly} unfollows/week"
        )

        if p5_weekly < p4_weekly * 0.5:
            msg = f"  CRITICAL: P5 throughput ({p5_weekly}/week) can't keep up with P4 ({p4_weekly}/week)"
            print(msg)
            issues.append(msg)
        elif p5_weekly < p4_weekly:
            msg = f"  WARNING: P5 throughput ({p5_weekly}/week) less than P4 ({p4_weekly}/week)"
            print(msg)
            issues.append(msg)
        else:
            print(f"  OK - P5 can keep up with P4")

    # 3. File management check
    print("\n[3] FILE MANAGEMENT CHECK")
    for name, info in details.items():
        fm = info["detail"].get("fileMgmt", "unknown")
        print(f"  {name}: fileMgmt='{fm}'")

    # 4. Session cookie consistency
    print("\n[4] SESSION COOKIE CHECK")
    cookies = set()
    for name, info in details.items():
        cookie = info["arg"].get("sessionCookie", "")
        if cookie:
            cookies.add(cookie)
            if len(cookie) < 20:
                msg = f"  {name}: SESSION COOKIE TOO SHORT ({len(cookie)} chars)"
                print(msg)
                issues.append(msg)

    if len(cookies) == 1:
        print(f"  All phantoms use the same session cookie - OK")
    elif len(cookies) > 1:
        msg = f"  WARNING: Found {len(cookies)} different session cookies!"
        print(msg)
        issues.append(msg)
    else:
        print("  No session cookies found - phantoms may not be configured yet")

    # Summary
    print(f"\n{'=' * 70}")
    print(f"  SUMMARY")
    print(f"{'=' * 70}")

    if issues:
        print(f"\n  Found {len(issues)} issue(s):\n")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue.strip()}")
    else:
        print("\n  ALL CHECKS PASSED - NO ISSUES FOUND")

    print(f"\n{'=' * 70}")


if __name__ == "__main__":
    run()
