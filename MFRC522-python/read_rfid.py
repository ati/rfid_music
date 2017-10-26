#!/usr/bin/env python
# -*- coding: utf8 -*-
#'{0:07b}'.format(1)

import RPi.GPIO as GPIO
import MFRC522
import signal
import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 7007

continue_reading = True

def send_udp(serial):
  sock = socket.socket(socket.AF_INET, # Internet
                      socket.SOCK_DGRAM) # UDP
  sock.sendto(str(serial), (UDP_IP, UDP_PORT))

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    # print "Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
# print "Welcome to the MFRC522 data read example"
# print "Press Ctrl-C to stop."

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:
    
    # Scan for cards    
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        # print "Card detected"
        # Get the UID of the card
        (status,uid) = MIFAREReader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == MIFAREReader.MI_OK:
            # Select the scanned tag
            if (MIFAREReader.MFRC522_SelectTag(uid) == 4): # Mifare ultralight

              sectors = []
              for i in range(0,4):
                sectors.append(MIFAREReader.MFRC522_Read(i))

              if (len(sectors) > 0 and isinstance(sectors[3], list)):
                """
                Card detected
                Size: 4
                  0   0   1   2   3
                  0  52   9  92 255
                  1  59 186  11 255
                  2 237 185 240 255
                  3 106  86   0 252
                  4   9  92 255  69
                  5 186  11 255 217
                  6 185 240 255 184
                  7  86   0 252  91
                  8  92 255  69  49
                  9  11 255 217  77
                10 240 255 184  93
                11   0 252  91   0
                12 255  69  49  32
                13 255 217  77 170
                14 255 184  93   0
                15 252  91   0   0

                card number = 2243106005 dec = 10000101101100110001010011010101 bin
                '{0:08b}{1:08b}{2:08b}{3:08b}{4:08b}'.format(184, 91, 49, 77, 93) = 1011*10000101101100110001010011010101*1101

                """

                padded = '{0:08b}{1:08b}{2:08b}{3:08b}{4:08b}'.format(sectors[3][6], sectors[3][7], sectors[3][8], sectors[3][9], sectors[3][10])
                serial = int(padded[4:36], 2)
                print serial            
                send_udp(serial)


