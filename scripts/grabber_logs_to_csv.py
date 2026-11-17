#!/usr/bin/env python3
"""Merge SLAMTEC simple_grabber angle/distance logs captured at known tilt angles.

Usage:
  python3 scripts/grabber_logs_to_csv.py --scan scans/level.txt:0 --scan scans/up15.txt:15 -o scans/tilted.csv

The tilt is a measured rotation about one fixed local X axis, not an arbitrary hand-held pose.
"""
import argparse
import csv
import re
from pathlib import Path

PATTERN = re.compile(r"theta:\s*([0-9]+(?:\.[0-9]+)?)\s+Dist:\s*([0-9]+(?:\.[0-9]+)?)")

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--scan", action="append", required=True, metavar="LOG:DEGREES",
                   help="One simple_grabber log and its signed tilt, e.g. scans/level.txt:0")
    p.add_argument("-o", "--output", type=Path, default=Path("scans/tilted.csv"))
    args = p.parse_args()
    entries = []
    for item in args.scan:
        try:
            path_str, angle_str = item.rsplit(":", 1)
            path, tilt = Path(path_str), float(angle_str)
        except (ValueError, TypeError):
            p.error(f"Invalid --scan {item!r}; expected LOG:DEGREES")
        if not -90 <= tilt <= 90:
            p.error(f"Unreasonable tilt {tilt}; expected -90 to 90 degrees")
        text = path.read_text(errors="replace")
        matches = PATTERN.findall(text)
        if not matches:
            p.error(f"No theta/Dist lines found in {path}; choose 'y' to print data when capturing")
        count = 0
        for a, distance in matches:
            # Keep raw measurements; downstream converter applies distance filtering.
            entries.append((a, distance, tilt))
            count += 1
        print(f"{path}: {count} measurements at tilt {tilt}°")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(("angle_deg", "distance_mm", "tilt_deg"))
        writer.writerows(entries)
    print(f"Wrote {len(entries)} readings to {args.output}")

if __name__ == "__main__":
    main()
