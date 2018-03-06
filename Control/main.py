from ps4 import PS4Controller
from Azubot import AzubotController

""" This class puts all required control components together and
    starts polling for control events. These events can be sent
    by any correctly implemented controller. Actions received are
    then sent to the AzubotController.
"""
class Application:
    # Catches actions requiring parameters to be passed.
    methodsWithParam = [ "setLeftSpeedNorm", "setRightSpeedNorm", "setHeadAngleHorizontal", "setHeadAngleVertical"]

    def __init__(self):
        # Initialize Azubot and Controller
        self.bot = AzubotController()
        #self.input = xboxController()
        self.input = PS4Controller()
        self.input.start()

        while True:
            # get actions from controller
            actions = self.input.getActions()
            for action in actions:
                if action is not None:
                    # differentiate between actions with and without parameters
                    if action in self.methodsWithParam:
                        # run action
                        result = getattr(self.bot, action)(actions[action])
                    else:
                        # run action
                        result = getattr(self.bot, action)()        
if __name__ == "__main__":
    Application()
