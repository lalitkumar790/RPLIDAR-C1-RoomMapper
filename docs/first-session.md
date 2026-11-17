# First session: connect to Pi and detect the C1

## 1. Network and SSH
Make sure your laptop and Pi are on the same trusted network. Enable SSH on the Pi using Raspberry Pi Imager or `sudo raspi-config`; use your Pi's actual username. From your laptop run:

```bash
ssh <pi-user>@raspberrypi.local
```

If that fails, get the Pi's LAN IP using `hostname -I` on the Pi or check the router's client list, then run `ssh <pi-user>@<pi-ip>`. A timeout generally means an IP/network/firewall problem; 'connection refused' usually means no SSH service is listening; 'permission denied' means credentials or authorized keys need checking.

## 2. Clone this repo on the Pi

```bash
sudo apt update
sudo apt install -y git usbutils
git clone https://github.com/lalitkumar790/RPLIDAR-C1-RoomMapper.git
cd RPLIDAR-C1-RoomMapper
bash scripts/pi_diagnostics.sh
```

Share the command output, except anything identifying your private network that you prefer not to share.

## 3. Plug in LiDAR
Connect the SLAMTEC C1 through its proper USB interface, keeping the sensor still and free to rotate. Re-run `bash scripts/pi_diagnostics.sh` and compare serial devices. `/dev/serial/by-id/...` paths are usually more stable than `/dev/ttyUSB0`.

## 4. Choose the right ROS installation
Do not blindly install ROS before checking `/etc/os-release` and `uname -m`. Ubuntu 24.04 arm64 supports ROS 2 Jazzy Debian packages. Raspberry Pi OS may require a different approach.

## 5. Confirm scan first, map later
Our initial goal is a real `sensor_msgs/msg/LaserScan` message on `/scan`. A complete occupancy-grid map requires motion estimates / odometry and correct transforms; a static LiDAR by itself is insufficient.

Do not publish your home floor plan or credentials in Git history without checking them.
