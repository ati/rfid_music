#!/bin/bash

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MUSIC_BASE_DIR=/home/pi/music
rfid="sudo $BASE_DIR/get_card_id.py"
mpc=/usr/bin/mpc
default_command="pause"


card_id=$($rfid) # blocking call
# echo "Got card_id=$card_id"
/bin/rm -f $MUSIC_BASE_DIR/card_id.*
/usr/bin/touch $MUSIC_BASE_DIR/card_id.$card_id

if [ -d "$MUSIC_BASE_DIR/$card_id" ]
then
  echo "Running updated playlist for $MUSIC_BASE_DIR/$card_id directory"
  $mpc clear
  $mpc add $card_id
  $mpc play
else
  $mpc $default_command
fi

