#include "wifi_config.h"
#include <WiFi.h>
#include <WebServer.h>

String ssid = "YOUR_WIFI";
String password = "YOUR_PASSWORD";
String apiUrl = "http://192.168.1.5:8000/upload";

WebServer server(80);

void handleRoot() {

String page = "<form action='/save'>";

page += "SSID:<input name='ssid'><br>";
page += "Password:<input name='pass'><br>";
page += "API URL:<input name='api'><br><br>";

page += "<button type='submit'>Save</button></form>";

server.send(200,"text/html",page);

}

void handleSave(){

ssid = server.arg("ssid");
password = server.arg("pass");
apiUrl = server.arg("api");

server.send(200,"text/html","Saved. Restart device.");

}

void startWiFi(){

WiFi.begin(ssid.c_str(),password.c_str());

while(WiFi.status()!=WL_CONNECTED){
delay(500);
}

Serial.println(WiFi.localIP());

}

void startConfigServer(){

server.on("/",handleRoot);
server.on("/save",handleSave);

server.begin();

}

void handleServer(){

server.handleClient();

}