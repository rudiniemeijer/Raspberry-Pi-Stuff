# Confgure for use with:
# VU-meter: sudo apt-get install python-sn3218  (Python 2)
#           sudo apt-get install python3-sn3218 (Python 3)

from speakerphat import clear, show, set_led

clear()
for x in range(10):
    set_led(x,255)
show()
