const byte dolls = 9;
const byte idx = 0;
int pins[dolls] = {PB12, PB13, PB14, PB15, PA8, PA9, PA10, PB6, PB7};

int lastIOn;
int lastXOn;
int lastIOff;
int lastXOff;
int timeElapsedOn = 0;
int timeElapsedOff = 0;

int state[dolls][dolls];

void setup() {
  Serial.begin(9600);
  for (byte c=0; c<dolls; c++) {
    pinMode(pins[c], INPUT_PULLUP);
    for (byte d=0; d<dolls; d++) {
      state[c][d] = 0;
    }
  }
}

void loop() {
  delay(100);
  for (byte c=0; c<dolls; c++) {
    pinMode(pins[c], OUTPUT);
    digitalWrite(pins[c], LOW);
    delay(10);
    for (byte r=0; r<dolls; r++) {
      if (r != c) {
        int i = min(r, c);
        int x = max(r, c);
        int s = state[i][x];
        if (digitalRead(pins[r])==LOW) {
          if (s != 1) {
            state[i][x] = 1;
            if (!(lastIOn == i && lastXOn == x) || timeElapsedOn > 5000) {
              Serial.print("1,");
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
            if (!(lastIOff == i && lastXOff == x) || timeElapsedOff > 5000) {
              Serial.print("0,");
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
}
