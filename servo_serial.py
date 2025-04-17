import cv2
import numpy as np
import serial
import time

# Serial Configuration
SERIAL_PORT = '/dev/ttyACM0'  # Check Arduino port
BAUD_RATE = 115200
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# Servo angle limits
MIN_ANGLE = 0
MAX_ANGLE = 180
CENTER_ANGLE = 90

# Current angles (tracked by Jetson)
# current_pan = CENTER_ANGLE`
# current_tilt = CENTER_ANGLE
# ANGLE_STEP = 2  # Degrees to move per adjustment

# Initialize camera
cap = cv2.VideoCapture(0)
ws, hs = 1280, 720
cap.set(3, ws)
cap.set(4, hs)

# def adjust_angle(offset, center):
    # if offset > center + 20:  # Dead zone ±20 pixels
    #     return ANGLE_STEP
    # elif offset < center - 20:
    #     return -ANGLE_STEP
    # return 0

def send_angles(pan, tilt):

    command = pan.to_bytes(2,'big') +  tilt.to_bytes(2,'big')
    # command = f"{pan},{tilt}\n"
    # ser.write(command.encode())
    ser.write(command)

try:
    while True:
        success, frame = cap.read()
        if not success:
            break

        # Processing (same as before)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 35, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        filtered_contours = [c for c in contours if cv2.contourArea(c)<70000]
        if filtered_contours:
            largest_contour = max(filtered_contours, key=cv2.contourArea)
            if 0 < cv2.contourArea(largest_contour) < 40000:
                x, y, w, h = cv2.boundingRect(largest_contour)
                obj_x = x + w//2
                obj_y = y + h//2

                # Calculate adjustments
                # pan_adj = adjust_angle(obj_x, ws//2)
                # tilt_adj = adjust_angle(obj_y, hs//2)

                cv2.rectangle(thresh, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.circle(thresh, (obj_x, obj_y), 15, (0, 0, 255), cv2.FILLED)

                cv2.rectangle(thresh, (620, 380), (660, 340), (0, 255, 0), 2)

                # Update angles with constraints
                # current_pan = max(MIN_ANGLE, min(MAX_ANGLE, current_pan + pan_adj))
                # current_tilt = max(MIN_ANGLE, min(MAX_ANGLE, current_tilt + tilt_adj))

                # Send to Arduino
                send_angles(obj_x, obj_y)

                print(cv2.contourArea(largest_contour))

                # print(obj_x,obj_y)
            

                # Visuals (saQme as before)
                # ... (drawing code remains unchanged)

        # Display and exit conditions (same as before)
        cv2.imshow("Tracking", thresh)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"Error: {e}")

finally:
    cap.release()
    cv2.destroyAllWindows()
    ser.close()