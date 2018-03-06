"""
    Interface for PWM class
    functionality described in azubot_gpio.py
"""
class IPwm:
    def __init__(self, pin_no):
        raise NotImplementedError

    def write(self, dutycycle_percent):
        raise NotImplementedError
