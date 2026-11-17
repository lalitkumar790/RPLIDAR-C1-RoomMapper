#!/usr/bin/env bash
# Read-only Raspberry Pi / RPLIDAR diagnostics. No sudo required.
set -u
echo "=== OS ==="
cat /etc/os-release 2>/dev/null || true
echo "=== Architecture / kernel ==="
uname -a
echo "=== RAM ==="
free -h
echo "=== Network interfaces ==="
hostname -I 2>/dev/null || true
echo "=== USB devices ==="
if command -v lsusb >/dev/null; then lsusb; else echo "lsusb not installed"; fi
echo "=== Persistent serial device names ==="
ls -l /dev/serial/by-id/ 2>/dev/null || true
echo "=== Candidate serial devices ==="
ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || true
echo "=== Current groups ==="
id -nG
echo "=== ROS ==="
if command -v ros2 >/dev/null; then command -v ros2; else echo "ros2 not on PATH"; fi
if [[ -d /opt/ros ]]; then ls /opt/ros; else echo "No /opt/ros installation found"; fi
echo "=== Done ==="
