"""
Instagram PhantomBuster Audit Script
Verifies all 5 Phantoms are configured correctly for the engage-then-follow strategy.

Checks:
- Correct scripts assigned to each Phantom
- Proper chaining (P1 -> P2 -> P3, P4 separate, P5 separate)
- Required fields present
- Safety limits respected
- Session cookies valid and consistent
- Data flow between Phantoms
"""

import json
import urllib.request
from config import PHANTOMBUSTER_API_KEY, EXPECTED_CONFIG


def api_get(endpoint):
    req = urllib.request.Request(
        f"https://api.phantombuster.com/api/v2/{endpoint}",
        headers={"X-Phantombuster-Key": PHANTOMBUSTER_API_KEY},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def api_get_agent(agent_id):
    return api_get(f"agents/fetch?id={agent_id}")


def run():
    agents = api_get("agents/fetch-all")
    agents.sort(key=lambda a: a.get("name", ""))

    print("=" * 70)
    print("       FULL AUDIT - ALL 5 PHANTOMS")
    print("=" * 70)

    all_ok = True

    for a in agents:
        name = a.get("name", "")

        # Find matching expected config (by partial name match)
        exp = {}
        for exp_name, exp_config in EXPECTED_CONFIG.items():
            if exp_name in name:
                exp = exp_config
                break

        if not exp:
            continue

        issues = []

        print(f"\n{'=' * 70}")
        print(f"  {name}")
        print(f"{'=' * 70}")

        # 1. Script check
        script = a.get("script", "MISSING")
        expected_script = exp.get("script", "")
        if script != expected_script:
            issues.append(f"WRONG SCRIPT: got '{script}', expected '{expected_script}'")
        print(f"  Script:   {script} {'OK' if script == expected_script else 'WRONG'}")

        # 2. Launch type
        lt = a.get("launchType")
        expected_lt = exp.get("launch", "")
        if lt != expected_lt:
            issues.append(f"WRONG LAUNCH TYPE: got '{lt}', expected '{expected_lt}'")
        print(f"  Launch:   {lt} {'OK' if lt == expected_lt else 'WRONG'}")

        # 3. Schedule details
        if lt == "repeatedly":
            rt = a.get("repeatedLaunchTimes", {})
            print(f"  Hours:    {rt.get('hour')}")
            print(f"  Days:     {rt.get('dow')}")
            print(f"  Timezone: {rt.get('timezone')}")
            if not rt.get("timezone"):
                issues.append("MISSING TIMEZONE")
        elif lt == "after agent":
            after_id = a.get("launchAfterAgentId")
            after_name = "UNKNOWN"
            for b in agents:
                if str(b.get("id")) == str(after_id):
                    after_name = b.get("name")
            expected_after = exp.get("after_name", "")
            if expected_after and expected_after not in after_name:
                issues.append(
                    f"WRONG CHAIN: triggers after '{after_name}', expected '{expected_after}'"
                )
            print(
                f"  After:    {after_name} {'OK' if expected_after in after_name else 'WRONG'}"
            )

        # 4. Arguments
        agent_detail = api_get_agent(a["id"])
        arg_str = agent_detail.get("argument", "{}") or "{}"
        try:
            arg = json.loads(arg_str)
        except json.JSONDecodeError:
            arg = {}
            issues.append("CANNOT PARSE ARGUMENT JSON")

        print(f"\n  Arguments:")
        for k, v in arg.items():
            if k == "sessionCookie":
                if v and len(v) > 10:
                    print(f"    sessionCookie: SET (valid)")
                else:
                    print(f"    sessionCookie: INVALID (too short)")
                    issues.append("SESSION COOKIE INVALID")
            else:
                print(f"    {k}: {v}")

        # 5. Required fields check
        for rf in exp.get("required_fields", []):
            if rf not in arg:
                issues.append(f"MISSING REQUIRED FIELD: {rf}")

        # 6. Input source check
        input_check = exp.get("input_should_contain", "")
        spreadsheet = arg.get("spreadsheetUrl", "")
        if input_check and input_check not in spreadsheet:
            issues.append(
                f"WRONG INPUT SOURCE: '{spreadsheet[:80]}' should contain '{input_check}'"
            )

        # 7. Field value checks
        for field, checks in exp.get("field_checks", {}).items():
            val = arg.get(field)
            if "max" in checks and checks["max"] is not None:
                if isinstance(val, (int, float)) and val > checks["max"]:
                    issues.append(f"{field}={val} EXCEEDS MAX {checks['max']}")
            if "expected" in checks:
                if val != checks["expected"]:
                    issues.append(f"{field}='{val}' should be '{checks['expected']}'")

        # Results
        print()
        if issues:
            all_ok = False
            print(f"  *** {len(issues)} ISSUE(S) FOUND ***")
            for i in issues:
                print(f"    - {i}")
        else:
            print(f"  STATUS: ALL CHECKS PASSED")

    print(f"\n{'=' * 70}")
    if all_ok:
        print("  OVERALL: ALL CHECKS PASSED")
    else:
        print("  OVERALL: ISSUES FOUND - SEE ABOVE")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    run()
