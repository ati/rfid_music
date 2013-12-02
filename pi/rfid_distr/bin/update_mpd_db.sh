#!/bin/bash

MUSIC_DIR=/home/pi/music

if [ -f "$MUSIC_DIR/update" ]
then
    /usr/bin/mpc update
    /bin/rm -f "$MUSIC_DIR/update"
fi
