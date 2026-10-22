#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm;

#define NUM_SERVOS 5

#define SERVO_MIN 100
#define SERVO_MAX 600

int servoPins[NUM_SERVOS] = {11,12,13,14,15};
int currentAngle[NUM_SERVOS] = {90, 90, 90, 90, 90};

void setup() {
  Serial.begin(9600);

  pwm.begin();
  pwm.setPWMFreq(50);

  delay(500);


  for (int i = 0; i < NUM_SERVOS; i++) {
    setServoAngle(servoPins[i], currentAngle[i]);
  }

  
}

void loop() {
  if (Serial.available()) {
    String msg = Serial.readStringUntil('\n');
    msg.trim();

    int targetAngles[NUM_SERVOS];
    int idx = 0;
    int start = 0;

    for (int i = 0; i <= msg.length(); i++) {
      if (i == msg.length() || msg.charAt(i) == ',') {
        if (idx < NUM_SERVOS) {
          targetAngles[idx] = constrain(msg.substring(start, i).toInt(), 0, 180);
          idx++;
        }
        start = i + 1;
      }
    }

    if (idx == NUM_SERVOS) {
      sweepTo(targetAngles);
      Serial.println("Recieved");
    } else {
      Serial.println("ERROR: expected " + String(NUM_SERVOS) + " values, got " + String(idx));
    }
  }
}

void sweepTo(int targets[NUM_SERVOS]) {
  bool stillMoving = true;

  while (stillMoving) {
    stillMoving = false;

    for (int i = 0; i < NUM_SERVOS; i++) {
      if (currentAngle[i] < targets[i]) {
        currentAngle[i]++;
        stillMoving = true;
      } else if (currentAngle[i] > targets[i]) {
        currentAngle[i]--;
        stillMoving = true;
      }
      setServoAngle(servoPins[i], currentAngle[i]);
    }

    delay(10);
  }
}

void setServoAngle(uint8_t channel, int angle) {
  angle = constrain(angle, 0, 180);
  int pulse = map(angle, 0, 180, SERVO_MIN, SERVO_MAX);
  pwm.setPWM(channel, 0, pulse);
}