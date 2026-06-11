#include <Arduino.h> 

#define LED_GREEN   25
#define LED_YELLOW  26
#define LED_RED     27
#define BUZZER      32


void allOff() {
  digitalWrite(LED_GREEN,  LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_RED,    LOW);
  digitalWrite(BUZZER,     LOW);   
}

void activeBuzzerBeep(int times, int onMs = 150, int offMs = 100) {
  for (int i = 0; i < times; i++) {
    digitalWrite(BUZZER, HIGH);
    delay(onMs);
    digitalWrite(BUZZER, LOW);
    delay(offMs);
  }
}

void blinkLED(int pin, int times, int delayMs) {
  for (int i = 0; i < times; i++) {
    digitalWrite(pin, HIGH); delay(delayMs);
    digitalWrite(pin, LOW);  delay(delayMs);
  }
  digitalWrite(pin, HIGH);   
}

void emergencyAlert() {
  for (int i = 0; i < 12; i++) {
    digitalWrite(LED_RED, HIGH);
    digitalWrite(BUZZER,  HIGH);
    delay(100);
    digitalWrite(LED_RED, LOW);
    digitalWrite(BUZZER,  LOW);
    delay(80);
  }
  digitalWrite(LED_RED, HIGH);  // leave red ON
}

void startupSequence() {
  int pins[] = {LED_GREEN, LED_YELLOW, LED_RED};
  for (int pin : pins) {
    digitalWrite(pin, HIGH); delay(200);
    digitalWrite(pin, LOW);  delay(100);
  }
  activeBuzzerBeep(1, 80);
}

void handleCommand(char cmd) {
  allOff();
  switch (cmd) {

    case 'I': 
      digitalWrite(LED_GREEN, HIGH);
      activeBuzzerBeep(1, 80);
      Serial.println("{\"ack\":\"INFO\",\"led\":\"green\"}");
      break;

    case 'W':  
      blinkLED(LED_YELLOW, 3, 200);
      activeBuzzerBeep(2, 150, 100);
      Serial.println("{\"ack\":\"WARNING\",\"led\":\"yellow\"}");
      break;

    case 'C': 
      blinkLED(LED_RED, 5, 120);
      activeBuzzerBeep(3, 150, 100);
      Serial.println("{\"ack\":\"CRITICAL\",\"led\":\"red\"}");
      break;

    case 'E': 
      emergencyAlert();
      Serial.println("{\"ack\":\"EMERGENCY\",\"led\":\"red_alarm\"}");
      break;

    case '0':  
      allOff();
      Serial.println("{\"ack\":\"CLEAR\"}");
      break;

    default:
      break;
  }
}

void setup() {
  Serial.begin(9600);
  pinMode(LED_GREEN,  OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_RED,    OUTPUT);
  pinMode(BUZZER,     OUTPUT);

  allOff();
  startupSequence();

  Serial.println("{\"status\":\"ready\",\"device\":\"EnviroSense-Actuator-v1\"}");
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = (char)Serial.read();
    handleCommand(cmd);
  }
}
