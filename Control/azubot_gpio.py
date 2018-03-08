from IPin import IPin
from IServo import IServo
from IPwm import IPwm
from IAzubot import IAzubot
import time
from pygame import mixer # Load sound library
import pigpio

# Initialize connection to local pigpio server
pi=pigpio.pi(port=8888)

# Create Custom Error for hardware interaction
class AccessError(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)

# Class handling pwm signals for speed control of the chain drive 
class PWMAccess(IPwm):
    maxVal = 255
    
    # sets the corresponding pwm pin as output
    def __init__(self, IO_Nr):
        global pi
        self.IO_Nr = IO_Nr
        pi.set_mode(self.IO_Nr, pigpio.OUTPUT)

    # changes pwm dutycycle (chain drive speed)
    def write(self, dutycycle_percent):
        global pi
        pi.set_PWM_dutycycle(self.IO_Nr, dutycycle_percent*self.maxVal/100)

    # turns pwm on and therefor moves chaindrive	
    def start(self, dutycycle_percent):
        self.write(dutycycle_percent)

    # Stops the chain drive (sets pwm to 0)	
    def stop(self):
        self.write(0)
		
# Class handling communication with servos (control of the head)
class ServoAccess(IServo):
    def __init__(self, IO_Nr, minAngle=-30, maxAngle=30, minPulsewidth=500, maxPulsewidth=2500, midPulsewidth=1500):
        global pi    
        self.IO_Nr = IO_Nr
        pi.set_mode(self.IO_Nr, pigpio.OUTPUT)

        pi.set_servo_pulsewidth(self.IO_Nr, 0) # initialize and switch off
        self.minAngle = minAngle
        self.maxAngle = maxAngle
        self.minPulsewidth = minPulsewidth
        self.maxPulsewidth = maxPulsewidth
        self.midPulsewidth = midPulsewidth

    # Sets the minimal angle of the servo to prevent overbending the cables
    def setMin(self, minAngle):
        self.minAngle = minAngle
        self.checkConsistency()

    # Sets the maximal angle of the servo to prevent overbending the cables
    def setMax(self, maxAngle):
        self.maxAngle = maxAngle
        self.checkConsistency()

    # check if settings are reasonable
    def checkConsistency(self):
        global pi 
        if self.minAngle > self.maxAngle:
            pi.set_servo_pulsewidth(self.IO_Nr, 0)
            return False

    # sets the angle of servo to be taken if it is in the given min/max range
    def setAngle(self, angle):
        global pi 
        if self.minAngle <= angle <= self.maxAngle:
            pi.set_servo_pulsewidth(self.IO_Nr, self.getPulsewidthFromAngle(angle))
    
    # centers the servos
    def reset(self):
        global pi
        pi.set_servo_pulsewidth(self.IO_Nr, 1500)
    
    # converts angle to pulsewidth
    def getPulsewidthFromAngle(self, angle):
        if angle < 0:
            return self.midPulsewidth - abs(self.midPulsewidth-self.minPulsewidth)*angle/self.minAngle
        elif angle > 0:
            return self.midPulsewidth + abs(self.midPulsewidth-self.maxPulsewidth)*angle/self.maxAngle
        else:
            pi.set_servo_pulsewidth(self.IO_Nr, self.midPulsewidth)
            time.sleep(0.05)
            return 0
      
# Handling gpio Acess for light etc.
class IOAccess(IPin):

    OUTPUT = 1
    INPUT = 2
    
    # Initializes gpio as input or output
    def __init__(self,IO_Nr,Mode):
        global pi
        if Mode != IOAccess.OUTPUT and Mode != IOAccess.INPUT:
            raise ValueError
        else:
            self.IO_Nr = IO_Nr
            self.Mode = pigpio.OUTPUT if Mode == IOAccess.OUTPUT else pigpio.INPUT
            pi.set_mode(self.IO_Nr,self.Mode)

    # Read State of pin
    def read(self):
        global pi
        return pi.read(self.IO_Nr)

    # set pin to specific state
    def write(self,value):
        global pi
        if self.Mode != IOAccess.OUTPUT:
            raise AccessError("No writing access on an input")
        else:
            pi.write(self.IO_Nr,value)


# Class initializing speaker offering to play sounds
class SoundPlayer:

    #default directory where sounds can be placed. 
    soundDirectory = '/home/pi/sounds/' 

    # initializes connection to soundcard
    def __init__(self):
        mixer.init()

    # play sounds from sd card
    def play(self, soundFile):
        mixer.music.load(self.soundDirectory+soundFile)
        mixer.music.play()