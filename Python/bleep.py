# pip install rpio
from RPIO import PWM

PWM.setup()
PWM.init_channel(dma_channel = 0)
