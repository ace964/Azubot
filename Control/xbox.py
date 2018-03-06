#
# Xbox Controller for Azubot
# running under linux. Requires any xbox driver
# edge detection is not required, because it is integrated
# in the xbox driver
#
import pygame
import time
from IController import IController

class xboxController(IController):
    """Class representing the PS4 controller. Pretty straightforward functionality."""
    hatToAction = {}
    buttonToAction = {}
    axisToAction = {}
    controller = None

    # Button Mapping
    buttonX = 2
    buttonY = 3
    buttonA = 0
    buttonB = 1
    buttonLB = 4
    buttonRB = 5
    buttonStart = 7
    buttonBack = 6
    buttonPS = 8
    buttonLStick = 9
    buttonRStick = 10
    # Stick and Trigger Mapping 
    stickLX = 0
    stickLY = 1
    stickRX = 3
    stickRY = 4
    triggerL = 2
    triggerR = 5
    
    # startup method initializing controller and device    
    def start(self):    
        # map controller keys as action to be run
        self.axisToAction[self.triggerL] = "setLeftSpeedNorm"
        self.axisToAction[self.triggerR] = "setRightSpeedNorm"
        self.axisToAction[self.stickRX] = "setHeadAngleHorizontal"
        self.axisToAction[self.stickRY] = "setHeadAngleVertical"
        self.axisToAction[self.stickLX] = None
        self.axisToAction[self.stickLY] = None
        
        self.buttonToAction[self.buttonLB] = "inverseLeftSpeed"
        self.buttonToAction[self.buttonRB] = "inverseRightSpeed"
        self.buttonToAction[self.buttonA] = "playHupe"
        self.buttonToAction[self.buttonB] = "playCantinaBand"
        self.buttonToAction[self.buttonX] = "toggleLightInfrared"
        self.buttonToAction[self.buttonY] = "toggleLightVisible"
        self.buttonToAction[self.buttonStart] = "playBootup"
        self.buttonToAction[self.buttonBack] = "playEngineStart"
        self.buttonToAction[self.buttonPS] = None
        self.buttonToAction[self.buttonLStick] = None
        self.buttonToAction[self.buttonRStick] = None
        
        # init
        pygame.init()
        pygame.joystick.init()
        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()
    
    # This function converts input signals to actions that are run by the main class.    
    def getActions(self):
        actions = {};
        for event in pygame.event.get():
            # handle stick event
            if event.type == pygame.JOYAXISMOTION:
                # differentiate betweed triggers and sticks (because of different value range required)
                if (event.axis == self.triggerL or event.axis == self.triggerR):
                    if event.axis in self.axisToAction: actions[self.axisToAction[event.axis]] = (50*(round(event.value,2) + 1))
                else:
                    if event.axis in self.axisToAction: actions[self.axisToAction[event.axis]] = round(event.value,2)*100
            # handle button down event
            elif event.type == pygame.JOYBUTTONDOWN:
                print("button PRESSED")
                if event.button in self.buttonToAction: actions[self.buttonToAction[event.button]] = True
            # handle button released event
            elif event.type == pygame.JOYBUTTONUP:
                # handle LB and RB button differently to create hold functionality
                if (event.button == self.buttonLB or event.button == self.buttonRB):
                    if event.button in self.buttonToAction: actions[self.buttonToAction[event.button]] = True
        return actions
           
