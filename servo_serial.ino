#include <Servo.h>

Servo panServo;
Servo tiltServo;

int panAngle = 90;
int tiltAngle = 120;
  int off_x;
  int off_y;

void setup() {
  Serial.begin(115200);
  panServo.attach(8);  // Connect pan servo to pin 9
  tiltServo.attach(10); // Connect tilt servo to pin 10
  panServo.write(panAngle);
  tiltServo.write(tiltAngle);
}

void loop() {
  if (Serial.available() >=4) {
//    String data = Serial.readStringUntil('\n');
//    int commaIndex = data.indexOf(',');
    
//       off_x = data.substring(0, commaIndex).toInt();
//       off_y = data.substring(commaIndex+1).toInt();
         off_x = (Serial.read()<<8)|Serial.read();

          off_y = (Serial.read()<<8)|Serial.read();
         
        Serial.print(off_x);
        Serial.print(",");
        Serial.println(off_y);

//    
//    if (commaIndex > 0) {
   
//
//  
//  if(off_x >= 660 && off_y<= 340 ){
//    panServo.write(--panAngle);
//    tiltServo.write(++tiltAngle);
//    
//    }
//
//    if(off_x <= 620 && off_y<= 340){
//    panServo.write(++panAngle);
//    tiltServo.write(++tiltAngle);
//    
//    }
//
//    if(off_x >= 660 && off_y>= 380 ){
//    panServo.write(--panAngle);
//    tiltServo.write(--tiltAngle);
//    
//    }
//
//    if(off_x <= 620 && off_y>= 380 ){
//    panServo.write(++panAngle);
//    tiltServo.write(--tiltAngle);
//    
//    }
//
//    else {
//      panServo.write(panAngle);
//     tiltServo.write(tiltAngle);
//      }
        if(off_x >= 1200) panAngle -=10;
     else if(off_x >= 900) panAngle -=5;
     else if(off_x >= 660) panAngle -=1;
     else if(off_x <= 200) panAngle +=10;
     else if(off_x <= 400) panAngle +=5;
     else if(off_x <= 600) panAngle +=1;

     if(off_y <= 90) tiltAngle += 10;
     else if(off_y <= 200) tiltAngle +=5;
     else if(off_y <= 320) tiltAngle +=1;
     else if(off_y >=680) tiltAngle -=10;
     else if(off_y >=500) tiltAngle -=5;
     else if(off_y >=400) tiltAngle -=1;


     panServo.write(panAngle);
     tiltServo.write(tiltAngle);
    
    
//      
//      panAngle = constrain(panAngle, 0, 180);
//      tiltAngle = constrain(tiltAngle, 0, 180);
//      
//      panServo.write(panAngle);
//      tiltServo.write(tiltAngle);
    }
  
}
