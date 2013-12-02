// This sketch reads RFID card ID and sends it as HTTP request to preconfigured website
// Author: Alexander Nikolaev (variomap@gmail.com)
#include <EtherCard.h>
#define LED 2

// ethernet interface mac address, must be unique on the LAN
static byte mymac[] = { 0x74,0x69,0x69,0x2D,0x30,0x31 };
static byte myip[] = { 192,168,1,25 };
static byte hisip[] = { 192,168,1,10 };
byte Ethernet::buffer[700];
char website[] PROGMEM = "192.168.1.10";

unsigned char rfid_id[4];
byte rfid_id_byte_count = 0;


// called when the client request is complete
static void my_callback (byte st, word off, word len) {
  // nothing to do so far
}


void blink_ok()
{
  digitalWrite(LED, HIGH);
  delay(200);
  digitalWrite(LED, LOW);
  delay(700);
}

void blink_error()
{
  for (int i = 0; i < 3; i++)
  {
    digitalWrite(LED, HIGH);
    delay(50);
    digitalWrite(LED, LOW);
    delay(300);
  }
}

void setup () {
  // led
  pinMode(LED, OUTPUT);
  digitalWrite(LED, HIGH);

  if (ether.begin(sizeof Ethernet::buffer, mymac) != 0) 
    blink_error();
    
  if (!ether.staticSetup(myip, hisip))
    blink_error();
  
   ether.copyIp(ether.hisip, hisip);
   ether.hisport = 19000;
   
   while (ether.clientWaitingGw())
     ether.packetLoop(ether.packetReceive());

  // rfid
  delay(1000);
  Serial.begin(9600);
  delay(10);
  Serial.write(0x02); // send command "simple receive" to rfid
  delay(100);
  
  rfid_id_byte_count = 0;
  
  digitalWrite(LED, LOW);
}


void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read(); 
    if (rfid_id_byte_count < 4)
    {
      rfid_id[rfid_id_byte_count++] = inChar;
    }
  }
}


void loop () {
  ether.packetLoop(ether.packetReceive());
  
  if (4 == rfid_id_byte_count)
  { 
    char rfid_urlencoded[16];
    sprintf(rfid_urlencoded, "%02X.%02X.%02X.%02X", rfid_id[0], rfid_id[1], rfid_id[2], rfid_id[3]);
    ether.browseUrl(PSTR("/rfid/1/"), rfid_urlencoded, website, my_callback);
    blink_ok();
    
    rfid_id_byte_count = 0;
  }
}
