#!/usr/bin/env python

import datetime
import piezonoises
from time import sleep
import scrollphathd
from scrollphathd.fonts import font5x5
#import geocoder

print("Scroll pHAT HD Alarm Clock")
# Nieuwe comment

BRIGHTNESSHI = 0.5
BRIGHTNESSLO = 0.1
BRIGHTNESS = BRIGHTNESSHI

alarm_hour = 6
alarm_minute = 30
in_alarm_state = False

scrollphathd.rotate(degrees=180)
#scrollphathd.clear()
#scrollphathd.set_pixel(0, 0, BRIGHTNESS)
#scrollphathd.show()

#g = geocoder.ip('me')
#print(g.latlng)

prev_second = -1
prev_minute = -1
prev_hour = -1

while True:
    scrollphathd.clear()
    now = datetime.datetime.now()
    hour, minute, second = now.hour, now.minute, now.second

    if ((hour >= 20) and (hour <=23)) or ((hour >= 0) and (hour <= 7)):
        BRIGHTNESS = BRIGHTNESSLO
    else:
        BRIGHTNESS = BRIGHTNESSHI

    # For testing purposes, set alarm time one minute from now
    if prev_second == -1: # This happens just once
        alarm_hour = hour
        alarm_minute = minute + 1

    display_hours = '%02d' % hour
    display_minutes = '%02d' % minute
    display_time = display_hours + ":" + display_minutes

    # Display the time (HH:MM) in a 5x5 pixel font
    scrollphathd.write_string(
        display_time,
        x=0, # Align to the left of the buffer
        y=0, # Align to the top of the buffer
        font=font5x5, # Use the font5x5 font we imported above
        brightness=BRIGHTNESS # Use our global brightness value
    )

    if (hour == alarm_hour) and (minute == alarm_minute):
        in_alarm_state = True
    else:
        in_alarm_state = False # Max one minute in alarm state

    if in_alarm_state:
        if minute != prev_minute:
            print("** ALARM **")
            strobe = True
            for x in range(0,17, 2):
                scrollphathd.set_pixel(x, 6, 1)
            scrollphathd.show()
            piezonoises.tune_one()

        if strobe:
            for x in range(0, 17, 8):
                scrollphathd.set_pixel(x, 6, 1)
            strobe = False
        else:
            strobe = True

    # Clear the colon on even seconds
    if second % 2 == 0:
        scrollphathd.clear_rect(8, 0, 1, 5)

    scrollphathd.show()
    prev_hour = hour
    prev_minute = minute
    prev_second = second

    sleep(0.1)
