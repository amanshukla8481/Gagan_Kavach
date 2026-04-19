# 🛡️ Gagan_Kavach (Jetson_AI)

> **Ground-to-Air Defense Inspired Object Tracking Laser Cannon**  
> A vision-based autonomous turret system for real-time aerial target detection and laser designation.

---

## 📝 Description

**Gagan_Kavach** is an AI-powered defense simulation system that mimics a ground-to-air defense mechanism. Starting from black-object thresholding, the project has evolved into a full **CSRT-tracked, PID-controlled autonomous turret** capable of tracking any user-selected region of interest — not just black objects.

The system uses computer vision to detect and track aerial objects (drones, projectiles) and automatically aims a laser cannon at the target using servo motors controlled by an Arduino microcontroller.

---

## 🧠 Core Technologies

| Layer | Technology |
|---|---|
| Object Detection & Tracking | OpenCV CSRT (`cv2.legacy.TrackerCSRT_create()`) |
| Control Algorithm | PID Controller (Proportional-Integral-Derivative) |
| Vision Host | Python 3.x |
| Microcontroller Firmware | Arduino (C++) |
| Serial Communication | PySerial |
| Camera Input | Webcam (960×540) |
| Laser Designation | Common laser module |
| Physical Design | SolidWorks 3D-modelled cannon structure |

---

## 🔧 Hardware Components

| Component | Specification |
|---|---|
| Vision Host | Jetson Nano (or any Python-capable host) |
| Microcontroller | Arduino UNO / Nano (ATmega328P) |
| Servo Motors | MG995 / MG996R (pan & tilt axes) |
| Camera | Webcam mounted on cannon muzzle (960×540) |
| Laser Module | Standard 5V laser module |
| Power Supply | External supply for servos and laser |
| Chassis | 3D-printed / SolidWorks-designed turret structure |

---

## 🧰 Software & Libraries

```
Python 3.x
├── opencv-python        # CSRT tracking & frame processing
├── numpy                # Array and matrix operations
├── pyserial             # Serial communication to Arduino
└── (optional) imutils   # Frame utilities

Arduino IDE (C++)
└── Servo.h              # PWM servo control
```

---

## ⚙️ How It Works

### System Pipeline

```
Webcam (960×540)
      │
      ▼
Frame Capture & Preprocessing
      │  (optional resolution downscale for 28–30 FPS throughput)
      ▼
CSRT Tracker (OpenCV)
      │  → Bounding box → Centre pixel (cx, cy)
      ▼
Error Calculation
      │  off_x = cx − frame_width/2
      │  off_y = cy − frame_height/2
      ▼
PID Controller (on Arduino / Python)
      │  Output = Kp·e + Ki·∫e·dt + Kd·(de/dt)
      ▼
Serial Command (9600 baud)
      │  "{off_x},{off_y}\n"
      ▼
Arduino Firmware
      │  → Servo PWM signals
      ▼
MG995 Pan & Tilt Servos ──► Laser locks onto target
```

### Detection Logic (Original / Fallback Mode)

1. Each frame is converted to grayscale.
2. Pixels with intensity `< 35` are classified as the black target object.
3. If the target appears in the **right half** of the frame, the Arduino receives a rotation command.
4. The servo rotates until the object is centred.
5. Once centred, servo movement stops and the laser locks on.

### CSRT Tracking Mode (Current)

1. On startup, the user draws a bounding box around any target via `cv2.selectROI()`.
2. CSRT tracks the selected region across frames using spatial reliability maps.
3. Centre coordinates are sent over serial to the Arduino every frame.
4. A `±80-pixel deadband` prevents jitter when the target is near-centred.
5. The laser fires only after the target has been centred for **3 consecutive frames** (hysteresis lock-on).

---

## 📂 Repository Structure

```
Gagan_Kavach/
├── vision/
│   ├── servo_serial.py          # Main vision + CSRT tracking script
│   └── black_object_detect.py   # Original threshold-based detector
├── firmware/
│   └── servo_control.ino        # Arduino sketch: serial parse + PID + PWM
├── calibration/
│   ├── pid_tuning.py            # PID gain tuning helper
│   └── bore_sight.py            # Camera–laser alignment calibration
├── design/
│   └── cannon_assembly.SLDPRT   # SolidWorks cannon structure
└── README.md
```

---

## ▶️ How to Run

### 1. Flash Arduino Firmware

```bash
# Open in Arduino IDE and upload:
firmware/servo_control.ino
```

### 2. Connect Hardware

- Connect servos and laser to external power supply.
- Connect Arduino to host machine via USB.
- Mount webcam on cannon muzzle.

### 3. Run Vision Host

```bash
# Install dependencies
pip install opencv-python numpy pyserial

# Run CSRT tracker (current version)
python3 vision/servo_serial.py

# OR run original black-object detector
python3 vision/black_object_detect.py
```

### 4. Select Target

- A live camera window opens.
- **Draw a bounding box** around your target using the mouse (`cv2.selectROI`).
- Press **Space / Enter** to confirm. The turret begins tracking automatically.

---

## 📊 Performance (Lab Validated)

| Metric | Result |
|---|---|
| End-to-End Latency | 85 ms |
| Linear Tracking Accuracy | 95% |
| Lock-On Time | 1.2 seconds |
| Post-Occlusion Recovery | 78% |
| Processing Throughput | 28–30 FPS |
| Human Reaction Time (baseline) | 200–300 ms |

---

## 📷 Demo

> 🚧 Photos and video demo coming soon — upload to `/assets/` and link here.

```markdown
![Turret demo](assets/demo.gif)
```

---

## 🔬 Research Report

A full technical report for this project was submitted to the **Digital Image Processing Laboratory, MNNIT — Session 2025–26** (Group 6).

Key academic references used in this project:

- Lukezic et al., *"Discriminative Correlation Filter Tracker with Channel and Spatial Reliability"*, CVPR 2017.
- Åström & Hägglund, *Advanced PID Control*, ISA, 2006.
- Ziegler & Nichols, *"Optimum Settings for Automatic Controllers"*, ASME, 1942.
- Bishop & Welch, *"An Introduction to the Kalman Filter"*, UNC-Chapel Hill, TR 95-041, 2001.

---

## 💡 Future Improvements

- [ ] **YOLOv8 integration** — class-specific detection (person, drone, vehicle) instead of color/region selection.
- [ ] **Kalman Filter predictor** — improve post-occlusion recovery from 78% by predicting target trajectory during full occlusion.
- [ ] **Dynamixel servo upgrade** — replace MG995/MG996R hobby servos to eliminate backlash and improve slew precision.
- [ ] **Adaptive PID** — gain-scheduling that adjusts Kp and Ki dynamically based on target velocity.
- [ ] **Multi-target tracking** — extend to SORT/DeepSORT for simultaneous tracking of multiple objects.
- [ ] **GUI / mobile remote control** — real-time override and manual targeting interface.
- [ ] **GPU acceleration** — enable full 1280×720 processing without frame rate drop.
- [ ] **Multi-modal sensing** — integrate ultrasonic or radar distance data for low-visibility targeting.

---

## ⚠️ Disclaimer

This project is a **simulation and educational system only**. It is intended for computer vision research, robotics coursework, and hobbyist learning. The laser used is a low-power module for demonstration purposes. **Do not use this system to target people, animals, aircraft, or any real-world entity.**

---

## 📄 License

MIT License — see `LICENSE` for details.

---

*Built by Group 6 — MNNIT Digital Image Processing Lab, 2025–26.*
