#!/usr/bin/env python3

# apt install python3-pip

import subprocess
#from subprocess import call
import os
import time
import smbus
import struct
import gpiod


# Choose a gain of 1 for reading voltages from 0 to 4.09V.
#  –   1 = +/-4.096V
# See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.

# value max 2048 (= 4.096V)
# 3.20V ~ 1599
# 2047 - 1599 = 448
# 448/4.48 = 100 (~ percentage)

refresh = 10 #refresh battery status every x seconds
shutdown_level = 1 # shutdown piComputer at x%
warning_level = 5

barWidth, icOn, icOff, warn, plug = 5, '■', '┄', '△', '⚡'

def cancelShutdown(msg):
    subprocess.call('shutdown -c --no-wall', shell=True)
    notification = f'dunstify -t 1500 -h {dunstTag} "{msg}" "Shutdown canceled."'
    subprocess.call(notification, shell=True)

def readVoltage(bus):

     address = 0x36
     read = bus.read_word_data(address, 2)
     swapped = struct.unpack("<H", struct.pack(">H", read))[0]
     voltage = swapped * 1.25 /1000/16
     return voltage


def readCapacity(bus):

     address = 0x36
     read = bus.read_word_data(address, 4)
     swapped = struct.unpack("<H", struct.pack(">H", read))[0]
     capacity = swapped/256
     return capacity


bus = smbus.SMBus(1)

PLD_PIN = 6
chip = gpiod.Chip('gpiochip4')
pld_line = chip.get_line(PLD_PIN)
pld_line.request(consumer="PLD", type=gpiod.LINE_REQ_DIR_IN)

while True:
    #adc = Adafruit_ADS1x15.ADS1015()
    #adc0 = readCapacity(bus) # battery value
    adc1 = pld_line.get_value() # is it plug to AC?
    #level = round((adc0-1599)/4.48) # battery percentage
    level = round(readCapacity(bus))

    dunstTag = 'string:x-dunst-stack-tag:battery'

    # is a shutdown is scheduled? with no-wall option?
    sched_file = '/run/systemd/shutdown/scheduled'
    shutdown_sched = 0
    if os.path.isfile(sched_file):
        with open(sched_file) as f:
            warn_wall = int(f.readlines()[1].rstrip().split("=")[1])
    if os.path.isfile(sched_file) and warn_wall == 0:
        shutdown_sched = 1

    if adc1 != 1: # picomputer is not plugged to AC
 
        nicOn = round((level + 5) / 100 * barWidth)
        if nicOn < 0:nicOn = 0
        nicOff = barWidth - nicOn

        bar = icOn*nicOn + icOff*nicOff

        if shutdown_sched == 1:
          bar = (barWidth-1)*icOff+warn
          with open(sched_file) as f:
              usec_shutdown = int(f.readline().rstrip().split("=")[1]) / 1000000

          current_time = time.time()
          remain = round(usec_shutdown - current_time)
          notification = f'dunstify -u critical -h {dunstTag} "Low battery" "piComputer will shutdown in <b>{remain}s</b> if you do not plug it."'
          subprocess.call(notification, shell=True)
        elif level < shutdown_level:
            subprocess.call('shutdown -h --no-wall +2 2>/dev/null', shell=True)
            notification = f'dunstify -u critical -h {dunstTag} "Low battery" "piComputer will shutdown in <b>2 minutes</b> if you do not plug it."'
            subprocess.call(notification, shell=True)

        if level >= warning_level and shutdown_sched == 1:
            cancelShutdown("Enough power")

        if level < warning_level or shutdown_sched == 1:
            print("%{B#FF8700}%{F#232323}","{0} bat.{1}".format(bar,level),"%{B-}%{F-}", flush=True)
        else:
            print("{0} bat.{1}".format(bar,level), flush=True)

    else: # picomputer is plugged to AC
        if shutdown_sched == 1:
            cancelShutdown("AC plugged")
        print("{0} bat.{1}".format((barWidth-1)*icOff+plug,level), flush=True)

    time.sleep(refresh)
