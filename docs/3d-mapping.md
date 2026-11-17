# Turning the C1 into a 3D room scanner

The C1 is a **single-plane 2D LiDAR**. Its published 360-degree scan lies in a nearly horizontal plane when the unit is level; it cannot infer full room geometry from one stationary horizontal sweep.

## What we will build

### Phase A — Proof of concept with known tilts

1. Verify realistic ranges from `simple_grabber` (completed, with some invalid near-field readings).
2. Mount C1 solidly with a *known* tilt angle and stable pivot. Avoid hand-held scans; do not twist cables.
3. Capture one full revolution at each calibrated angle, such as -45°, -30°, -15°, 0°, 15°, 30°, 45°. Record each sample's `angle_deg,distance_mm,tilt_deg` and verify angle orientation. Each angle must be known **at measurement time**.
4. Convert synchronized measurement CSV to an ASCII PLY point cloud with `scripts/scans_to_ply.py`:
   `python3 scripts/scans_to_ply.py samples.csv -o room3d.ply`
5. Open `.ply` in CloudCompare, MeshLab, or Open3D on a workstation.

### Phase B — Motorized tilting assembly

- 3D-printed bracket with **supported tilt shaft and bearings**, sufficient clearance for spinning C1
- Metal-gear servo or geared stepper sized for the entire LiDAR/adapter/bracket torque, plus position feedback or homing
- Dedicated, correctly rated motor power supply with common signal ground; never drive a motor from Pi GPIO directly
- Controller (Pi PWM or ESP32), calibrated tilt angle feedback, timestamping, and preferably synchronized scan capture
- Mechanical hard stops, USB cable strain relief and safe tilt limits

**Geometry caution:** Script assumes rotation around local X through LiDAR optical center, with level zero-tilt plane XY. Real assemblies have physical offsets and axis misalignment, which must be measured and applied to each scan. A tilting C1 alone produces a *partial* view with occlusions, not true omnidirectional 3D lidar.

### Phase C — Multiple viewpoints

Move the rig to multiple measured poses and register overlapping clouds by odometry, targets, or ICP / SLAM. Save aligned clouds and only then try meshing the room. Texture/color requires a camera.

## Current hardware state

- Raspberry Pi 5 Model B Rev 1.0 / 2 GB / Debian 13 aarch64
- C1 on CP2102N at `/dev/ttyUSB0`
- SLAMTEC SDK built and one 360-degree scan with realistic readings obtained
- Motorized tilt rig, tilt-angle sensor, synchronization, and full 3D reconstruction **not yet built**

## Limitations

- Zeros or data below sensor's effective minimum range should be filtered; default script filtering is 0.15 m to 12 m.
- Do not commit private room point clouds to a public repository without consent.
- A fixed horizontal LiDAR scan is a 2D slice. Simply assigning artificial heights does **not** generate genuine 3D measurements.
- `scans_to_ply.py` expects real observations with real tilt angles; it does not capture serial data itself.
