#include "wifi_config.h"
#include "led_control.h"

void setup() {

  Serial.begin(115200);

  initLEDs();

  startWiFi();
  startServer();

}

void loop() {

  handleServer();

}