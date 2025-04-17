

## 🚀 Gagan_Kavach (Jetson_AI)  
*A Ground-to-Air Defense Inspired Black Object Tracking Laser Cannon*

---

### 📝 Description

**Gagan_Kavach** is an AI-powered defense simulation system that mimics a **ground-to-air defense mechanism**. It uses computer vision to detect **black-colored aerial objects** (like projectiles or drones) and automatically aims a **laser cannon** at the target using servo motors.

---

### 🧠 Core Technologies

- 🎯 **Object Detection**: Implemented using **OpenCV**
- ⚙️ **Servo Motor Control**: Managed via **Arduino (C++)**
- 📸 **Camera Input**: Standard **Lenovo Webcam** mounted on the cannon
- 💡 **Laser Firing**: Common laser module for targeting
- 🧰 **Design**: SolidWorks 3D-modeled physical cannon

---

### 🔧 Hardware Components

- Jetson Nano (or similar for running OpenCV)
- Arduino UNO/Nano
- MG995 Servo Motors
- Lenovo Webcam
- Common Laser Module
- External Power Supply (for servos and laser)
- 3D-printed or SolidWorks-designed cannon structure

---

### 🧰 Software & Libraries

- Python (for vision + control logic)
- OpenCV (`cv2`)
- NumPy
- Arduino IDE (C++)  
- PySerial (to send commands from Python to Arduino)

---

### ⚙️ How It Works

1. The webcam (mounted on the muzzle of the cannon) continuously captures frames.
2. Each frame is converted to **grayscale**, and a thresholding method is applied.
3. If an object has an intensity **< 35**, it is classified as a **black object**.
4. If the black object appears in the **right half** of the camera frame:
   - The system sends rotation commands to the Arduino via **serial communication**.
   - The **MG995 servo motor** rotates until the black object is centered.
5. Once centered, servo movement stops and the laser locks onto the target.

---

### ▶️ How to Run

1. Connect power to the servos and laser.
2. Upload the Arduino code (`servo_control.ino`) to your Arduino board.
3. On the Jetson Nano (or your host machine):
   ```bash
   python3 servo_serial.py
   ```
4. Watch the cannon scan for black objects and automatically aim the laser.

---

### 📷 Demo

*(Upload photos or a YouTube link here later)*  
🚧 *Coming soon...*

---

### 💡 Future Improvements

- Add tracking for multiple objects.
- Implement color-based selection instead of only black.
- Add auto-fire mechanism based on object movement.
- Integrate remote controls via GUI or mobile app.
