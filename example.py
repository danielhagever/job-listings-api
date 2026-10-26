#!/usr/bin/env python3
"""Search open jobs across company career sites, or rank companies by hiring pace, into a CSV.

Standard library only. Needs an Apify API token in APIFY_TOKEN
(free at https://console.apify.com/settings/integrations).

    export APIFY_TOKEN=apify_api_...
    python3 example.py                                   # inputs/data-engineers-berlin.json
    python3 example.py inputs/companies-surging.json     # one row per company
    python3 example.py --title "product manager" --remote --new-within 24h --max 50
"""
import argparse
import csv
import json
import os
import sys
import urllib.error
import urllib.request

ACTOR = "glitchbound~ats-jobs-search"
RUN_SYNC = f"https://api.apify.com/v2/acts/{ACTOR}/run-sync-get-dataset-items"
COLUMNS = {
    "jobs": ["title", "company", "location", "country", "workArrangement", "seniority",
             "postedAt", "firstSeen", "platform", "url"],
    "closed": ["title", "company", "location", "department", "firstSeen", "lastSeen",
               "closedOn", "daysOpen", "platform"],
    "companies": ["company", "openRoles", "opened7", "opened30", "closed30", "net30",
                  "platform", "boardUrl"],
}


def run(actor_input, token):
    """Start one run, wait for it, and return its rows (the call blocks up to 300 s)."""
    req = urllib.request.Request(
        RUN_SYNC, data=json.dumps(actor_input).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=330) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Apify answered {e.code}: {e.read().decode()[:300]}")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("input", nargs="?",
                    default=os.path.join(here, "inputs", "data-engineers-berlin.json"),
                    help="a JSON input file (default: inputs/data-engineers-berlin.json)")
    ap.add_argument("--title", action="append", help="words the title must contain; repeat to OR")
    ap.add_argument("--location", action="append", help="a place, e.g. berlin; repeat to OR")
    ap.add_argument("--remote", action="store_true", help="remote roles only")
    ap.add_argument("--new-within", choices=["24h", "3d", "7d", "30d"],
                    help="only roles first seen in this window")
    ap.add_argument("--max", type=int, help="stop after this many rows")
    ap.add_argument("--out", default="jobs.csv")
    args = ap.parse_args()

    token = os.environ.get("APIFY_TOKEN")
    if not token:
        sys.exit("Set APIFY_TOKEN first: https://console.apify.com/settings/integrations")

    if args.title or args.location or args.remote or args.new_within:
        actor_input = {"mode": "jobs"}
    else:
        with open(args.input) as f:
            actor_input = json.load(f)
    if args.title:
        actor_input["title"] = args.title
    if args.location:
        actor_input["location"] = args.location
    if args.remote:
        actor_input["workArrangements"] = ["remote"]
    if args.new_within:
        actor_input["newWithin"] = args.new_within
    if args.max:
        actor_input["maxResults"] = args.max

    mode = actor_input.get("mode", "jobs")
    rows = run(actor_input, token)
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS[mode], extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} {mode} rows written to {args.out}")
    for r in rows[:5]:
        if mode == "companies":
            print(f"  {r.get('company')}: {r.get('openRoles')} open, {r.get('opened7')} opened in 7 days")
        else:
            print(f"  {r.get('company')}: {r.get('title')} ({r.get('location')})")


if __name__ == "__main__":
    main()
