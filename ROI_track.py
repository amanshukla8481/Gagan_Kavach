import cv2
import serial
import time
from collections import deque

print("📦 Imports complete")


def main():
    # --- SERIAL INIT ---
    arduino = serial.Serial('COM17', 9600, timeout=5)
    time.sleep(2)
    print("✅ Arduino connected at 9600 baud")

    # --- CAMERA & TRACKER ---  
    # cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
    # cap = cv2.VideoCapture(1)
    #
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
    # cap.set(cv2.CAP_PROP_FPS, 30)
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("Camera not detected")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
    cap.set(cv2.CAP_PROP_FPS, 30)

    tracker = cv2.legacy.TrackerCSRT_create()
    bbox_initialized = False
    failure_count = 0
    max_failures = 3  # Reduced - try recovery sooner
    object_lost = False

    # --- AUTO REDETECTION ---
    object_template = None
    object_hist = None
    last_known_bbox = None
    search_expanded = False

    # --- SMOOTHING BUFFER ---
    avg_window = 8  # Light smoothing for speed
    x_vals, y_vals = deque(maxlen=avg_window), deque(maxlen=avg_window)

    # --- FRAME CONSTANTS ---
    FRAME_WIDTH = 960
    FRAME_HEIGHT = 540
    CENTER_X = FRAME_WIDTH // 2
    CENTER_Y = FRAME_HEIGHT // 2

    # --- RATE LIMITING ---
    last_send_time = 0
    # send_interval = 0.025  # 40Hz for good responsiveness
    send_interval = 0.05

    # --- VISUAL SETTINGS ---
    show_debug = True

    print("🚀 Camera-on-Servo Tracking Started")

    while True:
        timer = cv2.getTickCount()
        success, img = cap.read()

        if not success:
            print("⚠️ Failed to read frame")
            continue

        if img.shape[1] != FRAME_WIDTH or img.shape[0] != FRAME_HEIGHT:
            img = cv2.resize(img, (FRAME_WIDTH, FRAME_HEIGHT))

        key = cv2.waitKey(1) & 0xFF

        # Draw center crosshair
        if show_debug:
            cv2.line(img, (CENTER_X - 20, CENTER_Y), (CENTER_X + 20, CENTER_Y), (0, 255, 0), 2)
            cv2.line(img, (CENTER_X, CENTER_Y - 20), (CENTER_X, CENTER_Y + 20), (0, 255, 0), 2)
            cv2.circle(img, (CENTER_X, CENTER_Y), 20, (0, 255, 0), 2)

        # ROI selection
        if not bbox_initialized:
            cv2.putText(img, "Press 's' to select ROI", (50, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2)
            if key == ord('s'):
                bbox = cv2.selectROI("Object Tracking", img, False, False)
                if bbox[2] > 0 and bbox[3] > 0:
                    tracker.init(img, bbox)
                    bbox_initialized = True
                    x_vals.clear()
                    y_vals.clear()

                    # Store template and histogram for recovery
                    x, y, w, h = map(int, bbox)
                    object_template = img[y:y + h, x:x + w].copy()
                    object_roi = img[y:y + h, x:x + w]
                    hsv_roi = cv2.cvtColor(object_roi, cv2.COLOR_BGR2HSV)
                    object_hist = cv2.calcHist([hsv_roi], [0, 1], None, [50, 60], [0, 180, 0, 256])
                    cv2.normalize(object_hist, object_hist, 0, 255, cv2.NORM_MINMAX)
                    last_known_bbox = bbox

                    print("✅ ROI initialized - camera will track")

        elif key == ord('s'):
            tracker = cv2.legacy.TrackerCSRT_create()
            bbox = cv2.selectROI("Object Tracking", img, False, False)
            if bbox[2] > 0 and bbox[3] > 0:
                tracker.init(img, bbox)
                bbox_initialized = True
                failure_count = 0
                object_lost = False
                x_vals.clear()
                y_vals.clear()

                # Store template and histogram for recovery
                x, y, w, h = map(int, bbox)
                object_template = img[y:y + h, x:x + w].copy()
                object_roi = img[y:y + h, x:x + w]
                hsv_roi = cv2.cvtColor(object_roi, cv2.COLOR_BGR2HSV)
                object_hist = cv2.calcHist([hsv_roi], [0, 1], None, [50, 60], [0, 180, 0, 256])
                cv2.normalize(object_hist, object_hist, 0, 255, cv2.NORM_MINMAX)
                last_known_bbox = bbox
                search_expanded = False

                print("✅ ROI reinitialized")

        # Tracking
        else:
            success, bbox = tracker.update(img)

            if success:
                failure_count = 0
                object_lost = False

                x, y, w, h = map(int, bbox)

                cx = x + w // 2
                cy = y + h // 2

                cx = max(0, min(cx, FRAME_WIDTH - 1))
                cy = max(0, min(cy, FRAME_HEIGHT - 1))

                x_vals.append(cx)
                y_vals.append(cy)

                # cx_smooth = int(sum(x_vals) / len(x_vals))
                # cy_smooth = int(sum(y_vals) / len(y_vals))
                cx_smooth = cx
                cy_smooth = cy


                current_time = time.time()
                if current_time - last_send_time >= send_interval:
                    data = f"{cx_smooth},{cy_smooth}\n"
                    try:
                        arduino.write(data.encode())
                        last_send_time = current_time
                        if show_debug:
                            offset_x = cx_smooth - CENTER_X
                            offset_y = cy_smooth - CENTER_Y
                            print(f"→ Offset: ({offset_x:+4d}, {offset_y:+4d})")

                            print({cx,cy})


                    except serial.SerialException as e:
                        print(f"⚠️ Serial error: {e}")

                # Visual feedback
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
                cv2.circle(img, (cx_smooth, cy_smooth), 7, (0, 255, 255), 2)
                cv2.line(img, (cx, cy), (cx_smooth, cy_smooth), (255, 255, 0), 1)

                if show_debug:
                    offset_x = cx_smooth - CENTER_X
                    offset_y = cy_smooth - CENTER_Y
                    cv2.putText(img, f"Offset: ({offset_x:+4d}, {offset_y:+4d})",
                                (10, FRAME_HEIGHT - 40),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                    cv2.putText(img, f"Pos: ({cx_smooth}, {cy_smooth})",
                                (10, FRAME_HEIGHT - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            else:
                failure_count += 1

                # Try auto-recovery before declaring object lost
                if failure_count >= max_failures and object_hist is not None:
                    # Try to find object using color-based detection
                    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                    backproj = cv2.calcBackProject([hsv], [0, 1], object_hist, [0, 180, 0, 256], 1)

                    # Apply threshold and find contours
                    _, thresh = cv2.threshold(backproj, 50, 255, cv2.THRESH_BINARY)
                    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
                    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
                    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

                    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                    if contours:
                        # Find largest contour
                        largest_contour = max(contours, key=cv2.contourArea)
                        area = cv2.contourArea(largest_contour)

                        # If significant area found, reinitialize tracker
                        if area > 500:  # Minimum area threshold
                            x, y, w, h = cv2.boundingRect(largest_contour)
                            new_bbox = (x, y, w, h)

                            # Reinitialize tracker with found object
                            tracker = cv2.legacy.TrackerCSRT_create()
                            tracker.init(img, new_bbox)
                            failure_count = 0
                            object_lost = False
                            last_known_bbox = new_bbox

                            # Show recovery on screen
                            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 255), 3)
                            cv2.putText(img, "AUTO-RECOVERED", (x, y - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                            print("✅ Object auto-recovered!")
                        else:
                            object_lost = True
                    else:
                        object_lost = True
                else:
                    # Not enough failures yet, keep trying
                    pass

                if object_lost:
                    cv2.putText(img, "OBJECT LOST - Press 's' to reselect",
                                (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
                else:
                    cv2.putText(img, f"Searching... ({failure_count}/{max_failures})",
                                (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 165, 255), 2)

        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
        cv2.putText(img, f"FPS: {int(fps)}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        if bbox_initialized:
            status = "TRACKING" if not object_lost else "LOST"
            color = (0, 255, 0) if not object_lost else (0, 0, 255)
            cv2.putText(img, status, (FRAME_WIDTH - 150, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        cv2.imshow("Object Tracking", img)

        if key == ord(" ") or key == 27:
            break

        if key == ord('d'):
            show_debug = not show_debug
            print(f"Debug info: {'ON' if show_debug else 'OFF'}")

    print("🛑 Shutting down...")
    cap.release()
    cv2.destroyAllWindows()
    arduino.close()
    print("✅ Cleanup complete")


if __name__ == "__main__":
    main()
