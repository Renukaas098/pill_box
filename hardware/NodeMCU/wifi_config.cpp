#include "wifi_config.h"
#include "led_control.h"

#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

ESP8266WebServer server(80);

String ssid="";
String password="";

void handlePage(){

String page="<h2>NodeMCU Configuration</h2>";

page+="<form action='/save'>";

page+="WiFi SSID:<br>";
page+="<input name='ssid'><br>";

page+="WiFi Password:<br>";
page+="<input name='pass'><br><br>";

page+="Green LED Name:<br>";
page+="<input name='green'><br>";

page+="Blue LED Name:<br>";
page+="<input name='blue'><br><br>";

page+="<button type='submit'>Save</button>";

page+="</form>";

server.send(200,"text/html",page);

}

void handleSave(){

ssid = server.arg("ssid");
password = server.arg("pass");

setGreenName(server.arg("green"));
setBlueName(server.arg("blue"));

server.send(200,"text/html","Saved. Restart device.");

}

void handleDetect(){

String name = server.arg("name");

processDetection(name);

server.send(200,"text/plain","OK");

}

void startWiFi(){

if(ssid==""){

WiFi.softAP("NodeMCU_SETUP");

Serial.println("Connect to NodeMCU_SETUP");

}
else{

WiFi.begin(ssid.c_str(),password.c_str());

while(WiFi.status()!=WL_CONNECTED){
delay(500);
Serial.print(".");
}

Serial.println("");
Serial.println(WiFi.localIP());

}

}

void startServer(){

server.on("/",handlePage);
server.on("/save",handleSave);
server.on("/detect",handleDetect);

server.begin();

}

void handleServer(){

server.handleClient();

}