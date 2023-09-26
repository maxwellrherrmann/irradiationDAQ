#include <EEPROM.h>

String analogPinNames[NUM_ANALOG_INPUTS] = {"VREFA","VREFD","","","",""};
// String analogPinNames[NUM_ANALOG_INPUTS] = {"","VINA","VDDA","VOFS","VIND","VDDD"};
float LinearCorrectionDivisor = 0.0;//Slope of Measured value vs Supplied Voltage data (200.61 for 6 pin Arduino 205.37 for 5 pin arduino)
float LinearCorrectionOffSet =  0.0;//Negative Y Intercept of trend line on Measured value vs Supplied Voltage (1.7021 for 6 pin Arduino 5.1606 for 5 pin Arduino)

void setup() {
  EEPROM.get(0,LinearCorrectionDivisor);
  EEPROM.get(4,LinearCorrectionOffSet);
  Serial.begin(9600);
}

void loop() {
  while(Serial.available()>0){
    String message = Serial.readString();
    if(message.substring(0,15) == "measureVoltages"){
      for(int i = 0;i < NUM_ANALOG_INPUTS;i++){
        if(analogPinNames[i] != ""){
          int analogVal = analogRead(i+A0);
          if(analogVal == 0){
            Serial.print("," + String(0.0,3));
          }
          else{
            Serial.print("," + String(((analogVal)+LinearCorrectionOffSet)/LinearCorrectionDivisor,3));
          }
        }
      }
      Serial.println();
    }
    else if(message.substring(0,13) == "measureValues"){
      for(int i = 0;i < NUM_ANALOG_INPUTS;i++){
        if(analogPinNames[i] != ""){
          int analogVal = analogRead(i+A0);
          Serial.print("," + String(analogVal));
        }
      }
      Serial.println();
    }
    else if(message == "getDataHeaders"){
      //Serial.println(",VREFA,VREFD");//For 6 pin
      for(int i = 0; i < NUM_ANALOG_INPUTS; i++){
        if(analogPinNames[i] != ""){
          Serial.print(",");
          Serial.print(analogPinNames[i]);
        }
      }
      Serial.println();
    }
    else if(message == "getCorrection"){
      float slope = 0.0;
      float y_int = 0.0;
      Serial.print("MeasuredVal = Voltage*");
      EEPROM.get(0,slope);
      EEPROM.get(4,y_int);
      Serial.print(slope,5);
      Serial.print("-");
      Serial.println(y_int,5);
    }
    else if(message.substring(0,13) == "setCorrection"){
      int delIndex = message.indexOf(',');
      EEPROM.put(0,message.substring(13,delIndex).toFloat());
      EEPROM.put(4,message.substring(delIndex+1).toFloat());
      Serial.println("Done");
    }
    else{
      Serial.println(message);
    }
  }
}