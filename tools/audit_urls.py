#!/usr/bin/env python3
"""Check that every asset in the store is still served, and still itself.

Two passes:

  audit_urls.py           every URL answers (ranged GET of one byte, fast)
  audit_urls.py --deep    ...and the bytes downloaded still hash to the
                          sha256 the manifest recorded

Always a ranged GET, never a HEAD: several CDNs in this mod's history --
Steam's among them -- answer 200 to a HEAD for a file that is gone. Asking
for a byte range makes them actually look.

The fast pass is the one that belongs on a schedule. The deep pass moves
ninety megabytes and is for after a push, or when something smells wrong.

Exit code 0 when every file checked out, 1 otherwise, so a cron or a
dead man's switch can watch it.
"""

import argparse
import concurrent.futures
import csv
import hashlib
import os
import sys
import urllib.error
import urllib.request

RAW = "https://raw.githubusercontent.com/ironsquadronfr-hub/swl-assets/main/assets/"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(HERE, "MANIFEST.csv")
ASSETS = os.path.join(HERE, "assets")


def check(row, deep):
    """Return (file, ok, detail) for one manifest line."""
    url = RAW + row["fichier"]
    req = urllib.request.Request(url)
    if not deep:
        req.add_header("Range", "bytes=0-0")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            if r.status not in (200, 206):
                return row["fichier"], False, f"HTTP {r.status}"
            if not deep:
                return row["fichier"], True, ""
            body = r.read()
    except urllib.error.HTTPError as e:
        return row["fichier"], False, f"HTTP {e.code}"
    except Exception as e:  # timeout, DNS, reset
        return row["fichier"], False, type(e).__name__

    got = hashlib.sha256(body).hexdigest()
    if got != row["sha256"]:
        return row["fichier"], False, f"sha256 {got[:12]} != {row['sha256'][:12]}"
    if len(body) != int(row["octets"]):
        return row["fichier"], False, f"{len(body)} octets != {row['octets']}"
    return row["fichier"], True, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deep", action="store_true",
                    help="download each file and verify its sha256")
    ap.add_argument("--jobs", type=int, default=8)
    args = ap.parse_args()

    rows = list(csv.DictReader(open(MANIFEST)))

    # The manifest and the directory must say the same thing. A file on disk
    # that nothing lists would go up unnoticed and unchecked; a line with no
    # file behind it means an asset went missing before it was ever pushed.
    # Files only: the veil-backdrops folder lives under its own rules and is
    # not in the manifest (see the README).
    on_disk = {f for f in os.listdir(ASSETS)
               if f != ".DS_Store" and os.path.isfile(os.path.join(ASSETS, f))}
    listed = {r["fichier"] for r in rows}
    drift = False
    for f in sorted(on_disk - listed):
        print(f"  NON LISTÉ   {f}")
        drift = True
    for f in sorted(listed - on_disk):
        print(f"  MANQUANT    {f}")
        drift = True

    bad = []
    with concurrent.futures.ThreadPoolExecutor(args.jobs) as pool:
        for name, ok, detail in pool.map(lambda r: check(r, args.deep), rows):
            if not ok:
                print(f"  MORT        {name}  ({detail})")
                bad.append(name)

    how = "octet + sha256" if args.deep else "octet de tête"
    print(f"{len(rows)} assets sondés ({how}) : {len(rows) - len(bad)} vivants, "
          f"{len(bad)} morts")
    return 1 if (bad or drift) else 0


if __name__ == "__main__":
    sys.exit(main())
