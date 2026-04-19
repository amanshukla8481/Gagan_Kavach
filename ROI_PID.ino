#include <Servo.h>

Servo panServo;
Servo tiltServo;

const int LASER_PIN = 13;

String inputString = "";
int off_x = 480;
int off_y = 270;

// --- Servo starting positions ---
float panAngle  = 90;
float tiltAngle = 130;

// --- Smoothing ---
float smoothX = 480;
float smoothY = 270;

// --- Frame center ---
const float CENTER_X = 480.0;
const float CENTER_Y = 270.0;
// const float CENTER_Y = 150.0;

// --- Deadband ---
const float DEADBAND_X = 80.0;
const float DEADBAND_Y = 80.0;

// --- PID Gains ---
// const float Kp_pan  = 0.04;
const float Kp_pan  = 0.005;

const float Ki_pan  = 0.0005;   // small — just enough to fix steady offset
// const float Ki_pan  = 0.005;   // small — just enough to fix steady offset

// const float Kd_pan  = 0.08;
const float Kd_pan  = 0.0;


const float Kp_tilt = 0.03;
const float Ki_tilt = 0.0004;
// const float Kd_tilt = 0.06;
const float Kd_tilt = 0.0;


// --- Integral limits --- 
// CRITICAL: without this, integral winds up and servo lunges
const float INTEGRAL_MAX = 30.0;

// --- Max step per frame ---
const float MAX_STEP_PAN  = 3.0;
const float MAX_STEP_TILT = 3.0;

// --- PID state ---
float prevErrorX = 0, prevErrorY = 0;
float integralX  = 0, integralY  = 0;

void setup() {
  Serial.begin(9600);
  inputString.reserve(20);

  panServo.attach(9);
  tiltServo.attach(10);
  pinMode(LASER_PIN,OUTPUT);
  digitalWrite(LASER_PIN,LOW);



  panServo.write((int)panAngle);
  tiltServo.write((int)tiltAngle);

  Serial.println("PID Tracker Ready");
  delay(500);
}

void loop() {
   


   
  while (Serial.available()) {
    char c = Serial.read();

    if (c == '\n') {
      int commaPos = inputString.indexOf(',');

      if (commaPos > 0) {
        off_x = inputString.substring(0, commaPos).toInt();
        off_y = inputString.substring(commaPos + 1).toInt();

        // --- Smoothing — reduces jitter before PID sees it ---
        smoothX = 0.95 * off_x + 0.05 * smoothX;
        smoothY = 0.95* off_y + 0.05 * smoothY;

         // Tighter laser zone — only fires when truly locked
         

        // --- Error from center ---
        float errorX = smoothX - CENTER_X;
        float errorY = smoothY - CENTER_Y;
      bool isCentered = (abs(smoothX - CENTER_X) < DEADBAND_X) && 
                  (abs(smoothY - CENTER_Y) < DEADBAND_Y);

      digitalWrite(LASER_PIN, isCentered ? HIGH : LOW);

         
        //  digitalWrite(LASER_PIN,  HIGH );

        // Use same deadband as PID — perfectly in sync 
       
        // --- Deadband ---
        // Inside deadband: freeze servo AND reset integral
        // This is critical — integral must not accumulate when we are stable
        if (abs(errorX) < DEADBAND_X) {
          errorX = 0;
          integralX *= 0.85;  // bleed integral slowly, don't hard reset
        }
        if (abs(errorY) < DEADBAND_Y) {
          errorY = 0;
          integralY *= 0.85;
        }


        // --- Derivative ---
        float dX = errorX - prevErrorX;
        float dY = errorY - prevErrorY;

        // --- Integral ---
        // Only accumulate when OUTSIDE deadband
        // This prevents windup while stable
        if (abs(errorX) > 0) {
          integralX += errorX;
          integralX = constrain(integralX, -INTEGRAL_MAX, INTEGRAL_MAX);
        }
        if (abs(errorY) > 0) {
          integralY += errorY;
          integralY = constrain(integralY, -INTEGRAL_MAX, INTEGRAL_MAX);
        }

        // --- PID Correction ---
        float correctionPan  = 0;
        float correctionTilt = 0;

        if (abs(errorX) > 0) {
          correctionPan = Kp_pan * errorX 
                        + Ki_pan * integralX 
                        + Kd_pan * dX;
          correctionPan = constrain(correctionPan, -MAX_STEP_PAN, MAX_STEP_PAN);
          panAngle -= correctionPan;
          panAngle = constrain(panAngle, 0, 180);
        }

        if (abs(errorY) > 0) {
          correctionTilt = Kp_tilt * errorY 
                         + Ki_tilt * integralY 
                         + Kd_tilt * dY;
          correctionTilt = constrain(correctionTilt, -MAX_STEP_TILT, MAX_STEP_TILT);
          tiltAngle -= correctionTilt;
          tiltAngle = constrain(tiltAngle, 0, 180);
        }

        // --- Save error for next frame ---
        prevErrorX = errorX;
        prevErrorY = errorY;

        // --- Write to servos ---
        panServo.write((int)panAngle);
        tiltServo.write((int)tiltAngle);

        // --- Debug for Serial Plotter ---
        // Four lines: errorX, errorY, panAngle, tiltAngle
        Serial.print(errorX);
        Serial.print(",");
        Serial.print(errorY);
        Serial.print(",");
        Serial.print(panAngle);
        Serial.print(",");
        Serial.println(tiltAngle);
        
      }

      inputString = "";

    } else {
      inputString += c;
    }
  }
}
 
