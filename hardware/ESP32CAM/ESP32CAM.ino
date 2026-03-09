#include "wifi_config.h"
#include "camera_upload.h"

void setup() {

  Serial.begin(115200);

  startWiFi();        // connect to wifi
  startConfigServer();// start config page
  initCamera();       // initialize camera

}

void loop() {

  handleServer();     // handle config webpage

  sendFrame();        // capture and upload image

}