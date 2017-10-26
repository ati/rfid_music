#!/usr/bin/env python -u
# -*- coding: utf8 -*-
# sounds from http://www.zapsplat.com/
from __future__ import print_function
import os
import sys
import time
import glob
import signal
import re
import subprocess
import traceback
import nfc_read

import logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(asctime)s %(message)s')

DEBOUNCE_TO = 1.0 # seconds
USB_MOUNT_ROOT = '/media'
SOUNDS_DIR = '/home/pi/sounds'
TMP_DIR='/tmp'
PLAYLIST=os.path.join(TMP_DIR, 'playlists')
MPLAYER=['/usr/bin/mplayer', '--really-quiet', '--ao=alsa:device=default', '--nolirc', '--novideo', '--no-mouseinput']
APLAY=['/usr/bin/aplay', '--quiet']

mplayer_process = None
playlist = None
need_to_rescan_directories = False
keep_running = True

def coroutine(func):
  def start(*args,**kwargs):
    cr = func(*args,**kwargs)
    cr.next()
    return cr
  return start


def sig_handler(signum, frame):
  global need_to_rescan_directories
  if signum == signal.SIGUSR1:
    need_to_rescan_directories = True


def exit_handler(signum, frame):
  global keep_running
  keep_running = False
    

def play_sound(snd_id):
  logging.info("Sound '%s'"%snd_id)
  subprocess.Popen(APLAY + [os.path.join(SOUNDS_DIR, "%s.wav"%snd_id)])


def pause():
  global mplayer_process
  logging.info("Pause")
  if mplayer_process and (mplayer_process.poll() is None):
    mplayer_process.stdin.write("p")
  else:
    logging.info("Pause in non-playing state")


def play_next():
  logging.info("Playing next")
  if mplayer_process and (mplayer_process.poll() is None):
    mplayer_process.stdin.write(">")


def play_list(list_id):
  global mplayer_process, playlist

  logging.info("Playing '%s'"%list_id)
  new_playlist = os.path.join(PLAYLIST, str(list_id))
  if os.path.isfile(new_playlist):
    if mplayer_process and (mplayer_process.poll() is None):
      mplayer_process.stdin.write("q")
      mplayer_process.wait()
    
    mplayer_process = subprocess.Popen(MPLAYER + ["--playlist=%s/%d"%(PLAYLIST, list_id)], stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stdout)
    playlist = new_playlist
  else:
    play_sound('oops')
    pause()
    logging.info("Request to play unknown playlist")



def scan_directories():
  logging.info("Rescanning /media/usb*")
  res = {}

  if mplayer_process and (mplayer_process.poll() is None):
    mplayer_process.stdin.write("q")
    mplayer_process.wait()

  # remove previous playlists
  for f in glob.glob(os.path.join(PLAYLIST, '*')):
    os.remove(f)
 
  # create new playlist for each 
  for root, dirs, files in os.walk(USB_MOUNT_ROOT):
    for file in files:
      file_name = os.path.join(root, file)
      match = re.search('/(\d+)(/|\Z)', root)
      if match:
        serial = int(match.group(1))
        if serial in res:
          res[serial].append(file_name)
        else:
          res[serial] = [file_name]

    for serial in res:
      with open(os.path.join(PLAYLIST, str(serial)), 'w') as f:
        print("\n".join(sorted(res[serial])), file=f)

  play_sound('usb')


def init():
  if not (os.path.isfile(MPLAYER[0]) and os.access(MPLAYER[0], os.X_OK)):
    logging.info("'%s' executable not found, exitting"%MPLAYER[0])
    exit(1)

  play_sound('start')
  signal.signal(signal.SIGUSR1, sig_handler)
  signal.signal(signal.SIGTERM, exit_handler)
  os.path.exists(PLAYLIST) or os.mkdir(PLAYLIST)
  scan_directories()


def current_playlist_serial():
  return None if playlist is None else int(os.path.basename(playlist))


def is_playing_now(serial):
  return (playlist is not None) and (serial == current_playlist_serial()) and mplayer_process and (mplayer_process.poll() is None)


def card_click(serial, clicks):
  logging.info("%s, %i clicks"%(serial, clicks))
  if is_playing_now(serial):
    play_next() if clicks > 1 else pause()
  else:
    play_list(serial)


@coroutine
def click(serial, target=card_click):
  last_ts = time.time()
  current_serial = None
  clicks = 0

  while True:
    serial = (yield)
    now_ts = time.time()
    if (serial is None) and (current_serial is not None) and (now_ts - last_ts > DEBOUNCE_TO):
      target(current_serial, clicks)
      current_serial = None
      clicks = 0
    elif (serial is not None):
      play_sound('card')
      current_serial = serial
      last_ts = now_ts
      clicks += 1


def main():
  global need_to_rescan_directories

  clicker = click(None)
  for serial, ts in nfc_read.serials():
    if serial is not None:
      logging.info("%s, %f"%(serial, ts))
    clicker.send(serial)

    if need_to_rescan_directories: # set in SIGUSR1 signal handler
      need_to_rescan_directories = False
      scan_directories()

    if not keep_running:
      break


if __name__ == '__main__':
  init()
  while keep_running:
    try:
      main()
    except KeyboardInterrupt:
      logging.info("Bye")
      break
    except:
      traceback.print_exc(file=sys.stdout)

  if mplayer_process and (mplayer_process.poll() is None):
    mplayer_process.stdin.write("q")
    mplayer_process.wait()
  elif mplayer_process:
    mplayer_process.kill()

