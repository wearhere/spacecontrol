// rotating switches
int rs1 = PA5;
int rs2 = PA6;
int rs3 = PA3;

// try a button
int b_top_blue = PA0;
int b_top_white = PA1;
int b_top_green = PA2;
int b_top_yellow = PB9;

//small button
int b_left_blue = PB7;
int b_left_green = PB6;
int b_left_black = PB8;

// sliders
int slide1 = PA7;
int slide2 = PA4;

//try a triple switch
//int sw1 = PA1;

// more graceful?
// int peripherals[4] = [rs1, rs2, slide1, slide2]
//std::map<int, int> switchMap;

// state tracking
int rs1_val = LOW;
int rs2_val = LOW;
int rs3_val = LOW;

int btb_val = 0;
int btw_val = 0;
int btg_val = 0;
int bty_val = 0;

int blb_val = 0;
int blg_val = 0;
int blk_val = 0;

int slide1_val = LOW;
int slide2_val = LOW;
int sw1_val = LOW;

void setup() {
  Serial.begin(9600);
  pinMode(rs1, INPUT);
  pinMode(rs2, INPUT);
  pinMode(rs3, INPUT);
  
  pinMode(b_top_blue, INPUT_PULLUP);
  pinMode(b_top_white, INPUT_PULLUP);
  pinMode(b_top_green, INPUT_PULLUP);
  pinMode(b_top_yellow, INPUT_PULLUP);

  pinMode(b_left_blue, INPUT_PULLUP);
  pinMode(b_left_green, INPUT_PULLUP);
  pinMode(b_left_black, INPUT_PULLUP);
  
  pinMode(slide1, INPUT);
  pinMode(slide2, INPUT);
  //pinMode(sw1, INPUT);
}

void loop() {
  rs1_val = analogRead(rs1);
  rs2_val = analogRead(rs2);
  rs3_val = analogRead(rs3);
  
  btb_val = digitalRead(b_top_blue);
  btw_val = digitalRead(b_top_white);
  btg_val = digitalRead(b_top_green);
  bty_val = digitalRead(b_top_yellow);

  blb_val = digitalRead(b_left_blue);
  blg_val = digitalRead(b_left_green);
  blk_val = digitalRead(b_left_black);
  
  slide1_val = analogRead(slide1);
  slide2_val = analogRead(slide2);
  //sw1_val = digitalRead(sw1);
  
  // more graceful? str.join?
  Serial.print("rs1:");
  Serial.print(rs1_val);
  Serial.print(",rs2:");
  Serial.print(rs2_val);
  Serial.print(",rs3:");
  Serial.print(rs3_val);
  
  Serial.print(",btb:");
  Serial.print(btb_val);
  Serial.print(",btw:");
  Serial.print(btw_val);
  Serial.print(",btg:");
  Serial.print(btg_val);
  Serial.print(",bty:");
  Serial.print(bty_val);

  Serial.print(",blb:");
  Serial.print(blb_val);
  Serial.print(",blg:");
  Serial.print(blg_val);
  Serial.print(",blk:");
  Serial.print(blk_val);
  
  Serial.print(",slide1:");
  Serial.print(slide1_val);
  Serial.print(",slide2:");
  Serial.print(slide2_val);
  //Serial.print(",sw1:");
  //Serial.print(sw1_val);
  Serial.print("\n");
  delay(100);
}
