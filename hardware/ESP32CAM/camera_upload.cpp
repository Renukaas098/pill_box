#include "camera_upload.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include "esp_camera.h"

extern String apiUrl;

unsigned long lastSend = 0;

void initCamera(){

// camera configuration simplified

camera_config_t config;

config.frame_size = FRAMESIZE_QVGA;
config.pixel_format = PIXFORMAT_JPEG;

esp_camera_init(&config);

}

void sendFrame(){

if(millis() - lastSend < 2000) return;

camera_fb_t * fb = esp_camera_fb_get();

if(!fb) return;

HTTPClient http;

http.begin(apiUrl);

http.addHeader("Content-Type","image/jpeg");

http.POST(fb->buf, fb->len);

http.end();

esp_camera_fb_return(fb);

lastSend = millis();

}