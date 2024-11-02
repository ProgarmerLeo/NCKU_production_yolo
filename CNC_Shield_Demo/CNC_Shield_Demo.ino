/*
https://howtomechatronics.com/tutorials/arduino/stepper-motors-and-arduino-the-ultimate-guide/
https://blog.csdn.net/panjinliang066333/article/details/135224781
*/
#include <AccelStepper.h>
#define RUN false
#define EN 8
#define X_DIR 5
#define Z_DIR 7
#define X_STP 2
#define Z_STP 4

AccelStepper motor(1, 3, 6);
bool run = true;
bool defect = false;
String str;
String input = "INPUT";
String DEFECT = "DEFECT";

void step(boolean dir, byte dirPin, byte stepperPin, int steps) {
  digitalWrite(dirPin, dir);
  delay(50);
  for (int i = 0; i < steps; i++) {
    digitalWrite(stepperPin, HIGH);
    delayMicroseconds(800);
    digitalWrite(stepperPin, LOW);
    delayMicroseconds(800);
  }
}

void setup() {
  pinMode(X_DIR, OUTPUT);
  pinMode(X_STP, OUTPUT);
  pinMode(Z_DIR, OUTPUT);
  pinMode(Z_STP, OUTPUT);
  pinMode(EN, OUTPUT);
  digitalWrite(EN, LOW);
  Serial.begin(9600);
  motor.setMaxSpeed(1000);
}

void loop() {

  /*if (defect){
        defect = false;
        run = true;
    }*/
  if (run) {
    motor.setSpeed(180);
    motor.runSpeed();
    if (Serial.available()) {
      str = Serial.readStringUntil('\n');
      if (str == input) {
        step(true, Z_DIR, Z_STP, 175);
      } else if (str == DEFECT) {
        //run = false;
        //defect = true;
        step(false, X_DIR, X_STP, 200);
      } else if (str == "stop") {
        run = false;
      } else if (str == "run") {
        run = true;
      } else if (str == "EM_STOP_ON") {
        run = false;
      }
    }
  }
}
