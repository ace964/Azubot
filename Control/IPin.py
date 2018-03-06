"""
    Interface for pin class
    functionality described in azubot_gpio.py
"""
class IPin:
    def __init__(self, pin_no, mode):
        raise NotImplementedError

    def write(self, value):
        raise NotImplementedError
