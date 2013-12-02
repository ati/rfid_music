#!/bin/bash

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
mpg321='/opt/local/bin/mpg321 -R useless_parameter'
mpg321_fifo="$BASE_DIR/mpg321.fifo"
rfid="$BASE_DIR/get_card_id.py"
playlist="$BASE_DIR/playlist.pls"
default_command="pause"


function refresh_player() {
  [ -p $mpg321_fifo ] || mkfifo $mpg321_fifo


  if ! pgrep -q mpg321
  then
    $mpg321 < $BASE_DIR/mpg321.fifo
  fi
}


function update_playlist() {
  find $BASE_DIR/$1 -type f -name \*.mp3 > $playlist
}


killall mpg321
sleep 1
/bin/rm -f $mpg321_fifo

while true
do
  refresh_player

  card_id=$(rfid) # blocking call
  rm $BASE_DIR/card_id.*
  touch $BASE_DIR/card_id.$card_id

  if [ -d "$BASE_DIR/$card_id" ]
  then
    update_playlist $card_id
    echo load $playlist > $mpg321_fifo
  else
    echo $default_command > $mpg321_fifo
  fi

  sleep 2
done

