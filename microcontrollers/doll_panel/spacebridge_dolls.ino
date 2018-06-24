const byte touch = 15;
const byte testtubes = 3;
const byte idx = 0;
int pins[touch] = {PB12, PB13, PB14, PB15, PA8, PA9, PA10, PB6, PB7, PB8, PB9, PB11, PA7, PA6, PA3};
int syringe = PA7;
int syringe_key = 12;
int tubes[testtubes] = {PB10, PB1, PB0};
int color = -1;
int dick = PA4;

int lastIOn;
int lastXOn;
int lastIOff;
int lastXOff;
int timeElapsedOn = 0;
int timeElapsedOff = 0;
int timeElapsedTime = 5000;
int timeElapsedColor = 10000;

int state[touch][touch];
int dick_state = 0;

void setup() {
  Serial.begin(9600);
  for (byte c=0; c<touch; c++) {
    pinMode(pins[c], INPUT_PULLUP);
    for (byte d=0; d<touch; d++) {
      state[c][d] = 0;
    }
  }
  for (byte t=0; t<touch; t++) {
    pinMode(tubes[t], INPUT_PULLUP);
  }
  pinMode(dick, INPUT_PULLUP);
}

void loop() {
  delay(100);
  // Sensing Touch
  for (byte c=0; c<touch; c++) {
    pinMode(pins[c], OUTPUT);
    digitalWrite(pins[c], LOW);
    delay(10);
    for (byte r=0; r<touch; r++) {
      if (r != c) {
        int i = min(r, c);
        int x = max(r, c);
        int s = state[i][x];
        if (digitalRead(pins[r])==LOW) {
          if (s != 1) {
            state[i][x] = 1;
            if (!(lastIOn == i && lastXOn == x) || timeElapsedOn > timeElapsedTime) {
              if (i == syringe_key || x == syringe_key) {
                Serial.print(color);
              } else {
                Serial.print("1");
              }
              Serial.print(",");
              Serial.print(i);
              Serial.print(" ");
              Serial.print(x);
              Serial.print("\n");
              timeElapsedOn = 0;
            }
            lastIOn = i;
            lastXOn = x;
          }
        } else {
          if (s != 0) {
            state[i][x] = 0;
            if (!(lastIOff == i && lastXOff == x) || timeElapsedOff > timeElapsedTime) {
              if (i == syringe_key || x == syringe_key) {
                Serial.print("-1");
                color = -1;
              } else {
                Serial.print("0");
              }
              Serial.print(",");
              Serial.print(i);
              Serial.print(" ");
              Serial.print(x);
              Serial.print("\n");
              timeElapsedOff = 0;
            }
            lastIOff = i;
            lastXOff = x;
          }
        }
      }
    }
    timeElapsedOn = timeElapsedOn + 100;
    timeElapsedOff = timeElapsedOff + 100;
    pinMode(pins[c], INPUT_PULLUP);
  }

  // Sensing Test Tube Colors
  pinMode(syringe, OUTPUT);
  digitalWrite(syringe, LOW);
  delay(10);
  for (byte t=0; t<testtubes; t++) {
    if (digitalRead(tubes[t])==LOW) {
      color = t;
    }
  }
  pinMode(syringe, INPUT_PULLUP);

  // Sensing Clown Dick
  if (digitalRead(dick)==LOW && dick_state != 1) {
    Serial.print("1");
    Serial.print(",");
    Serial.print("15");
    Serial.print(" ");
    Serial.print("\n");
    dick_state = 1;
  } else if (digitalRead(dick)==HIGH && dick_state != 0) {
    Serial.print("0");
    Serial.print(",");
    Serial.print("15");
    Serial.print(" ");
    Serial.print("\n");
    dick_state = 0;
  }
}
