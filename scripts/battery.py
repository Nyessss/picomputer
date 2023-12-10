#!/usr/bin/env python3

import time
import board
import adafruit_max1704x
import os
import subprocess

i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
max17 = adafruit_max1704x.MAX17048(i2c)

barWidth, icOn, icOff, warn, plug = 5, '■', '┄', '△', '⚡'

refresh = 2 #refresh battery status every x seconds
shutdown_level = 1 # shutdown piComputer at x%
warning_level = 5
max17.quick_start = True


def cancelShutdown(msg):
    subprocess.call('shutdown -c --no-wall', shell=True)
    notification = f'dunstify -t 1500 -h {dunstTag} "{msg}" "Shutdown canceled."'
    subprocess.call(notification, shell=True)

#print("Found MAX1704x with chip version",hex(max17.chip_version),"and id",hex(max17.chip_id),)

while True:
    voltage = round((max17.cell_voltage),2) # battery value
    level = round(max17.cell_percent) # battery percentage

    dunstTag = 'string:x-dunst-stack-tag:battery'

    # is a shutdown is scheduled? with no-wall option?
    sched_file = '/run/systemd/shutdown/scheduled'
    shutdown_sched = 0
    if os.path.isfile(sched_file):
        with open(sched_file) as f:
            warn_wall = int(f.readlines()[1].rstrip().split("=")[1])
    if os.path.isfile(sched_file) and warn_wall == 0:
        shutdown_sched = 1

    #if level < 101: # picomputer is not plugged to AC
 
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
            print("%{B#FF8700}%{F#232323}","{0} bat.{1} {2}V ".format(bar,level,voltage),"%{B-}%{F-}", flush=True)
     #   else:
      #      print("{0} bat.{1}".format(bar,level), flush=True)

    else: # picomputer is plugged to AC
        if shutdown_sched == 1:
            cancelShutdown("AC plugged")
        print("{0} bat.{1}".format((barWidth-1)*icOff+plug,level), flush=True)

    time.sleep(refresh)









    #print(f"Battery voltage: {max17.cell_voltage:.2f} Volts")
    #print(f"Battery state  : {max17.cell_percent:.1f} %")
    #print("%{B#FF8700}%{F#232323}","{0} bat.{1} {2}".format(bar,level,voltage),"%{B-}%{F-}", flush=True)
    #print("%{B#FF8700}%{F#232323}","{0} bat.{1} {2}".format(bar,max17.cell_percent,round(max17.cell_voltage),"%{B-}%{F-}", flush=True)
    #print("Voltage alert minimum = %0.2f V","{0} bat.{1}".format(bar,level),"and id",float(max17.cell_voltage))
    #time.sleep(2)