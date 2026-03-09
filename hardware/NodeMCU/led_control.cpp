#include "led_control.h"
#include <Arduino.h>

int greenPin = D1;
int bluePin  = D2;
int redPin   = D3;

String greenName = "";
String blueName  = "";

void initLEDs(){

  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
  pinMode(redPin, OUTPUT);

}

void setGreenName(String name){
  greenName = name;
}

void setBlueName(String name){
  blueName = name;
}

void processDetection(String name){

  digitalWrite(greenPin, LOW);
  digitalWrite(bluePin, LOW);
  digitalWrite(redPin, LOW);

  if(name == greenName){
    digitalWrite(greenPin, HIGH);
  }
  else if(name == blueName){
    digitalWrite(bluePin, HIGH);
  }
  else{
    digitalWrite(redPin, HIGH);
  }

}