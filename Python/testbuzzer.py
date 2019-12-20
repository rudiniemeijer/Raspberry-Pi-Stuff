import RPi.GPIO as GPIO # Importeer de GPIO bibliotheek.
import time ## Importeer de bibliotheek voor tijdfuncties
 
buzzer_pin = 22  # Geef het nummer van de pin op waar de speaker is aangesloten.
GPIO.setmode(GPIO.BCM) # GebruikBroadcom GPIO benaming van de pinnen.
GPIO.setup(buzzer_pin, GPIO.OUT) # Zet de speaker pin als uitgang.
 
print "Druk op CTRL+C om het programma te beeindigen."
 
try:
  while True:
    GPIO.output(buzzer_pin, True) # Zet speakerpin hoog.
    time.sleep(.3) # Wacht even.
    GPIO.output(buzzer_pin, False) # Zet speakerpin laag.
    time.sleep(.5) # Wacht even.
 
except KeyboardInterrupt:  
  GPIO.output(buzzer_pin, False) # Zet speakerpin laag.
  # GPIO netjes afsluiten
  GPIO.cleanup()
