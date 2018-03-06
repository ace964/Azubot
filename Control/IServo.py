"""
    Interface for Servo class
    functionality described in azubot_gpio.py
"""
class IServo:
    def __init__(self, IO_Nr, minAngle=-30, maxAngle=30, minPulsewidth=1000, maxPulsewidth=2000, midPulsewidth=1500):
        raise NotImplementedError

    def setMin(self, minAngle):
        raise NotImplementedError

    def setMax(self, maxAngle):
        raise NotImplementedError

    def setAngle(self, angle):
        raise NotImplementedError

