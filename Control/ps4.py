#
# Playstation Controller for Azubot
# running under linux. Requires ds4drv
#
import pygame
import time
from IController import IController

"""Class representing the PS4 controller. Pretty straightforward functionality."""
class PS4Controller(IController):
    hatToAction = {}
    buttonToAction = {}
    axisToAction = {}
    # old states for edge detection
    oldStates = {}
    for i in range(0, 15):
        oldStates[i] = False

    # create key/trigger/stick mappings
    buttonX = 0
    buttonY = 3
    buttonA = 1
    buttonB = 2
    buttonLB = 4
    buttonRB = 5
    buttonStart = 8
    buttonBack = 9
    buttonPS = 12
    buttonLStick = 10
    buttonRStick = 11
    buttonTouchpad= 13
    stickLX = 0
    stickLY = 1
    stickRX = 2
    stickRY = 5
    triggerL = 3
    triggerR = 4
    
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
        self.buttonToAction[self.buttonRStick] = "resetHeadPosition"
        self.buttonToAction[self.buttonTouchpad] = "playWagner"
        
        # init
        pygame.init()
        pygame.joystick.init()
        controller = None
        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()
        
    # This function converts input signals to actions that are run by the main class.
    def getActions(self):
        """Listen for events to happen"""
        actions = {};
        for event in pygame.event.get():
            # handle stick event
            if event.type == pygame.JOYAXISMOTION:
                # differentiate betweed triggers and sticks (because of different value range required)
                if (event.axis == self.triggerL or event.axis == self.triggerR): 
                    if event.axis in self.axisToAction: actions[self.axisToAction[event.axis]] = (50*(round(event.value,2) + 1))
                else:
                    if event.axis in self.axisToAction: actions[self.axisToAction[event.axis]] = round(event.value,2)*100
            # handle button pressed down event
            elif event.type == pygame.JOYBUTTONDOWN:
                # rising edge detection
                if (not self.oldStates[event.button]):
                    if event.button in self.buttonToAction: actions[self.buttonToAction[event.button]] = True
                self.oldStates[event.button] = True
            # handle button released event
            elif event.type == pygame.JOYBUTTONUP:
                # handle LB and RB button differently to create hold functionality
                if (event.button == self.buttonLB or event.button == self.buttonRB):
                    # bidirectional edge detection
                    if (self.oldStates[event.button]):
                        if event.button in self.buttonToAction: actions[self.buttonToAction[event.button]] = True
                        self.oldStates[event.button] = False
                self.oldStates[event.button] = False
        return actions