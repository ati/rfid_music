#!/usr/bin/env python -u
# -*- coding: utf8 -*-

import time
import signal
import socket
import RPi.GPIO as GPIO
import MFRC522

#import nfc_read
#for serial in nfc_read.serials():
#  print serial
def serials():
  # Create an object of the class MFRC522
  MIFAREReader = MFRC522.MFRC522()

  last_read = time.time()
  while True:
    # Scan for cards    
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
    since_last = time.time() - last_read
    last_read += since_last

    # If a card is found
    if status == MIFAREReader.MI_OK:
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
            yield (int(padded[4:36], 2), since_last)  # serial number and timestamp since last_read

    # If a card is not found
    else:
      yield (None, since_last)
      time.sleep(0.2)

