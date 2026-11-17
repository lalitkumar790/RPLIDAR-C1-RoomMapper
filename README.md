# RPLIDAR C1 RoomMapper

Indoor 2D laser scanning and experimental room mapping using a **Raspberry Pi 5 Model B (2 GB RAM)** and **SLAMTEC RPLIDAR C1**.

## Verified hardware (2026-11-17)

- Raspberry Pi 5 Model B Rev 1.0 (2 GB), Debian 13 Trixie aarch64
- SLAMTEC C1 USB bridge: Silicon Labs CP2102N at `/dev/ttyUSB0`
- Persistent device path: `/dev/serial/by-id/usb-Silicon_Labs_CP2102N_USB_to_UART_Bridge_Controller_6e2b4cb14931f11194fe8c5f30d20014-if00-port0`
- User `lalit` is already in `dialout`; ROS 2 is not installed
- **Next verification:** test live measurements with upstream SDK. USB detection alone does not confirm sensor data.

## 3D mapping extension

We now have a proof-of-concept coordinate conversion for **real, calibrated tilted scans**. See [3D scanning plan](docs/3d-mapping.md) and [CSV to PLY converter](scripts/scans_to_ply.py). A horizontal scan alone cannot make a genuine 3D map. No tilt hardware or multi-pose registration has been validated yet.

## Milestones

- [ ] M0 — Connect to Raspberry Pi by SSH, identify OS/architecture and USB serial adapter
- [ ] M1 — Run SLAMTEC's C1 ROS 2 driver and verify `/scan`
- [ ] M2 — Visualize the 360-degree scan in RViz (on a computer with a display)
- [ ] M3 — Supply reliable LiDAR motion estimates (odometry/scan matching), run SLAM, and save a room map

> **Important:** A stationary 2D LiDAR produces a live *scan*, not a complete room map. Building a consistent map while moving it requires a known horizontal scan plane and reliable relative motion estimates; odometry/IMU or suitable laser scan matching is required. Simply picking up and carrying the scanner is not guaranteed to work with default SLAM Toolbox.

## Hardware

- Raspberry Pi 5 Model B (2 GB RAM) with sufficient power and network access
- RPLIDAR C1 with its **compatible USB adapter/cable**
- A stable flat mount; keep spinning components unobstructed
- Optional later: wheel encoders, IMU, differential-drive base

## Start here — SSH and inspect the Pi

On the Pi, enable SSH via Raspberry Pi Imager settings or `sudo raspi-config` (Interface Options -> SSH). On your laptop, with both devices on the same trusted network:

```bash
ssh <pi-user>@raspberrypi.local
```

If mDNS doesn't work, find the Pi's LAN IP on your router or from its console and use `ssh <pi-user>@<pi-ip>`.

Then run:

```bash
cat /etc/os-release
uname -m
free -h
ls -l /dev/serial/by-id/ 2>/dev/null || true
ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || true
lsusb
```

**Do not assume the OS.** We will choose installation steps after verifying its release and architecture. For ROS 2 Jazzy, **Ubuntu 24.04 64-bit** is an especially straightforward supported choice; ROS 2 packages available on other Raspberry Pi OS versions vary.

## Native SDK scan test (Debian 13 / Raspberry Pi 5)

The simplest first step does not require ROS 2:

```bash
sudo apt update
sudo apt install -y git build-essential
cd ~
git clone https://github.com/Slamtec/rplidar_sdk.git
cd rplidar_sdk
make
ls output/Linux/Release/
./output/Linux/Release/ultra_simple --channel --serial /dev/ttyUSB0 460800
```

Stop the stream with Ctrl+C. Expect angle/distance measurements if the sensor is responding. If build output is located elsewhere, inspect the directory before trying another path. Position the unit safely with the rotating head unobstructed. The model's baud rate is 460800. If the test fails, collect the exact SDK output before changing configuration. See [upstream SDK](https://github.com/Slamtec/rplidar_sdk).

## ROS 2 Jazzy / Ubuntu 24.04 (only if we choose this OS later)

Install ROS 2 Jazzy following the [official ROS 2 Ubuntu instructions](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html). With ROS installed:

```bash
sudo apt update
sudo apt install -y python3-colcon-common-extensions ros-jazzy-slam-toolbox ros-jazzy-nav2-map-server
mkdir -p ~/rplidar_ws/src
cd ~/rplidar_ws/src
git clone https://github.com/Slamtec/sllidar_ros2.git
cd ~/rplidar_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

Launch the driver (adjust `serial_port` to the **actual** device path; the C1 uses 460800 baud by default):

```bash
ros2 launch sllidar_ros2 sllidar_c1_launch.py serial_port:=/dev/ttyUSB0
```

In another SSH session (source the same ROS environment):

```bash
source /opt/ros/jazzy/setup.bash
source ~/rplidar_ws/install/setup.bash
ros2 topic list
ros2 topic hz /scan
ros2 topic echo /scan --once
```

To view scans, use RViz on a Linux computer running a compatible ROS 2 distribution or a Pi with a desktop display. The upstream package also provides:

```bash
ros2 launch sllidar_ros2 view_sllidar_c1_launch.py
```

If serial permissions fail, check the relevant device's group and add your user to it (commonly `dialout`), then log out and back in. Do not use `chmod 777` on serial devices.

## Mapping — after motion tracking is solved

With a correct TF chain (`map -> odom -> base_link -> laser`) and a working odometry source, run:

```bash
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=false
```

When a valid map is being published on `/map`, save it:

```bash
mkdir -p ~/room_maps
ros2 run nav2_map_server map_saver_cli -f ~/room_maps/room_map
```

This should yield `room_map.pgm` and `room_map.yaml`. Mapping without an odometry source will require a separately tested scan-matching integration; it is **not** provided by the scanner driver.

## Repository layout

- `scripts/pi_diagnostics.sh` — read-only environment and connected-device checks
- `docs/first-session.md` — SSH-to-LiDAR checklist
- `maps/.gitkeep` — placeholder for future example maps (avoid publishing private floor plans without review)

## References

- [SLAMTEC ROS 2 driver](https://github.com/Slamtec/sllidar_ros2)
- [ROS 2 Jazzy installation](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html)
- [SLAM Toolbox](https://github.com/SteveMacenski/slam_toolbox)
- [Nav2 mapping tutorial](https://docs.nav2.org/rolling/tutorials/general_tutorials/navigation2_with_slam/navigation2_with_slam/)

**Status:** Starter project; no hardware test, scan, or room map has been completed yet.
