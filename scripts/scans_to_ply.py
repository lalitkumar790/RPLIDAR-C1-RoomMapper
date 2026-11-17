#!/usr/bin/env python3
"""Convert stationary, known-tilt 2D laser scan CSVs into a 3D ASCII PLY point cloud.

CSV columns: angle_deg,distance_mm,tilt_deg
Assumptions: LiDAR initial scanning plane XY, then rigid rotation about its *local X*
axis; its optical center lies on that rotation axis. A real offset requires calibration.
This is a proof of concept, not a registered room-scale SLAM reconstruction.
"""
import argparse
import csv
import math
from pathlib import Path

def convert(rows, min_m, max_m):
    pts = []
    for row in rows:
        a = math.radians(float(row["angle_deg"]))
        t = math.radians(float(row["tilt_deg"]))
        d = float(row["distance_mm"]) / 1000.0
        if not math.isfinite(d) or not min_m <= d <= max_m:
            continue
        # Local planar point (d cos a, d sin a, 0) rotated about X by t.
        x = d * math.cos(a)
        y = d * math.sin(a) * math.cos(t)
        z = d * math.sin(a) * math.sin(t)
        pts.append((x, y, z))
    return pts

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("csv", type=Path, help="CSV containing angle_deg,distance_mm,tilt_deg")
    p.add_argument("-o", "--output", type=Path, default=Path("room3d.ply"))
    p.add_argument("--min-range", type=float, default=0.15)
    p.add_argument("--max-range", type=float, default=12.0)
    args = p.parse_args()
    with args.csv.open(newline="") as f:
        reader = csv.DictReader(f)
        required = {"angle_deg", "distance_mm", "tilt_deg"}
        if not required.issubset(reader.fieldnames or []):
            p.error("CSV requires angle_deg,distance_mm,tilt_deg headers")
        pts = convert(reader, args.min_range, args.max_range)
    if not pts:
        p.error("No points remained after range filtering")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as f:
        f.write("ply\nformat ascii 1.0\n")
        f.write(f"element vertex {len(pts)}\n")
        f.write("property float x\nproperty float y\nproperty float z\nend_header\n")
        for xyz in pts:
            f.write("{:.6f} {:.6f} {:.6f}\n".format(*xyz))
    print(f"Saved {len(pts)} points to {args.output}")

if __name__ == "__main__":
    main()
