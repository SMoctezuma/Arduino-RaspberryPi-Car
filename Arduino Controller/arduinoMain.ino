#include <LiquidCrystal_I2C.h>

//www.elegoo.com

//    The direction of the car's movement
//  ENA   ENB   IN1   IN2   IN3   IN4   Description
//  HIGH  HIGH  HIGH  LOW   LOW   HIGH  Car is runing forward
//  HIGH  HIGH  LOW   HIGH  HIGH  LOW   Car is runing back
//  HIGH  HIGH  LOW   HIGH  LOW   HIGH  Car is turning left
//  HIGH  HIGH  HIGH  LOW   HIGH  LOW   Car is turning right
//  HIGH  HIGH  LOW   LOW   LOW   LOW   Car is stoped
//  HIGH  HIGH  HIGH  HIGH  HIGH  HIGH  Car is stoped
//  LOW   LOW   N/A   N/A   N/A   N/A   Car is stoped
LiquidCrystal_I2C lcd(0x27,2,1,0,4,5,6,7,3,POSITIVE);

void printTxt(String s) {
  lcd.clear();
  lcd.print(s);
}

//define L298n module IO Pin
#define ENA 5
#define ENB 6
#define IN1 7
#define IN2 8
#define IN3 9
#define IN4 11

void stopping(){
  digitalWrite(ENA,HIGH); //enable L298n A channel
  digitalWrite(ENB,HIGH); //enable L298n B channel
  digitalWrite(IN1,LOW); //set IN1 hight level
  digitalWrite(IN2,LOW);  //set IN2 low level
  digitalWrite(IN3,LOW);  //set IN3 low level
  digitalWrite(IN4,LOW); //set IN4 hight level
  Serial.println("stopped");//send message to serial monitor
  printTxt("stopped");
}

void forward(){
  digitalWrite(ENA,HIGH); //enable L298n A channel
  digitalWrite(ENB,HIGH); //enable L298n B channel
  digitalWrite(IN1,HIGH); //set IN1 hight level
  digitalWrite(IN2,LOW);  //set IN2 low level
  digitalWrite(IN3,LOW);  //set IN3 low level
  digitalWrite(IN4,HIGH); //set IN4 hight level
  Serial.println("Forward");//send message to serial monitor
  printTxt("Forward");
}

void back(){
  digitalWrite(ENA,HIGH);
  digitalWrite(ENB,HIGH);
  digitalWrite(IN1,LOW);
  digitalWrite(IN2,HIGH);
  digitalWrite(IN3,HIGH);
  digitalWrite(IN4,LOW);
  Serial.println("Back");
  printTxt("Back");
}

void left(){
  digitalWrite(ENA,HIGH);
  digitalWrite(ENB,HIGH);
  digitalWrite(IN1,LOW);
  digitalWrite(IN2,HIGH);
  digitalWrite(IN3,LOW);
  digitalWrite(IN4,HIGH);
  Serial.println("Left");
  printTxt("Left");
}

void fLeft(){
  digitalWrite(ENA,HIGH);
  digitalWrite(ENB,HIGH);
  digitalWrite(IN1,HIGH);
  digitalWrite(IN2,HIGH);
  digitalWrite(IN3,LOW);
  digitalWrite(IN4,HIGH);
  Serial.println("Left");
  printTxt("Left");
}

void right(){
  digitalWrite(ENA,HIGH);
  digitalWrite(ENB,HIGH);
  digitalWrite(IN1,HIGH);
  digitalWrite(IN2,LOW);
  digitalWrite(IN3,HIGH);
  digitalWrite(IN4,LOW);
  Serial.println("Right");
  printTxt("Right");
}

void fRight(){
  digitalWrite(ENA,HIGH);
  digitalWrite(ENB,HIGH);
  digitalWrite(IN1,HIGH);
  digitalWrite(IN2,HIGH);
  digitalWrite(IN3,HIGH);
  digitalWrite(IN4,LOW);
  Serial.println("Right");
  printTxt("Right");
}
//before execute loop() function,
//setup() function will execute first and only execute once
void setup() {
  lcd.begin(16,2);
  Serial.begin(9600);//open serial and set the baudrate
  pinMode(IN1,OUTPUT);//before useing io pin, pin mode must be set first
  pinMode(IN2,OUTPUT);
  pinMode(IN3,OUTPUT);
  pinMode(IN4,OUTPUT);
  pinMode(ENA,OUTPUT);
  pinMode(ENB,OUTPUT);
  printTxt("Car Starting");
}

char serial;
//Repeat execution
void loop() {
  if(Serial.available()) {
    serial = Serial.read();
    Serial.print(serial);
    switch(serial) {
      case '1':
        forward();
        break;
      case '2':
        fLeft();
        break;
      case '3':
        fRight();
        break;
      case '4':
        back();
        break;
      default:
      case '0':
        stopping;
        break;
    }
    //if(serial == '1') {
      //forward();
    //} else if(serial == '2') {
    //  left();
    //} else if(serial == '3') {
    //  right();
    //} else if(serial == '4') {
    //  back();
    //} else if(serial == '0') {
    //  stopping();
    //} else {
    //  printTxt("Received nothing");
    //}
  }
}
  //forward();  //go forward
  //delay(1000);//delay 1000 ms
  //back();     //go back
  //delay(1000);
  //left();     //turning left
  //delay(1000);
  //right();    //turning right
  //delay(1000);

