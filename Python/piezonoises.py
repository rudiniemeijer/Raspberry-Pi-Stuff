# Assumes a piezo plate has been connected between GND and pin 18
# Note that pin 18 is also labelled as '12', 'BCM 18 (PWM0)' or 'P1-12' and is on
# the second row of pins, 6th from the top

# gpiozero is not default on Lite Raspbian
# install with sudo apt-get install gpiozero

from gpiozero import PWMOutputDevice
from time import sleep
piezo_pin = 18
duty_cycle = 0.5
piezo = PWMOutputDevice(pin = piezo_pin, initial_value = 0, frequency = 440)

c4 = 262
d4 = 294
e4 = 330
f4 = 349
g4 = 392
a4 = 440
b4 = 494
c5 = 2 * c4
d5 = 2 * d4
e5 = 2 * e4
f5 = 2 * f4

tempo = 120 # Beats Per Minute

def tone(frequency, duration):
  piezo.frequency = frequency
  piezo.value = duty_cycle
  sleep(duration)
  piezo.off()

def ladder_up():
  duration = 0.1
  tone(c4, duration)
  tone(d4, duration)
  tone(e4, duration)
  tone(f4, duration)
  tone(g4, duration)
  tone(a4, duration)
  tone(b4, duration)
  tone(c5, duration)

def tune_one():
  melody = [[a4,4], [a4,4],  [a4,4], [f4,5], [c5,16],
    [a4,4], [f4,5], [c5,16], [a4,2], [e5,4], [e5,4], [e5,4],
    [f5,5], [c5,16], [a4,4], [f4,5], [c5,16], [a4,2]]

  for note in melody:
    f = note[0]
    d = ((1000 * (60 * 4 / tempo)) / float(note[1])) / 1000
    print("Playing %s, %s" % (f, d))
    tone(f, d)
    sleep(d * 1.2)

#tone(100, 1)
ladder_up()
#tune_one()
