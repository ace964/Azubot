"""
	Interface for Azubot
	functionality described in Azubot.py
"""
class IAzubot:
    def __init__(self):
        raise NotImplementedError

    def setLeftSpeed(self, value):
        raise NotImplementedError

    def setRightSpeed(self, value):
        raise NotImplementedError

    def setLeftSpeedNorm(self, value):
        raise NotImplementedError

    def setRightSpeedNorm(self, value):
        raise NotImplementedError

    def inverseLeftSpeed(self):
        raise NotImplementedError

    def inverseRightSpeed(self):
        raise NotImplementedError

    def getLeftSpeed(self):
        raise NotImplementedError

    def getRightSpeed(self):
        raise NotImplementedError

    def setHeadAngleHorizontal(self, value):
        raise NotImplementedError

    def setHeadAngleVertikal(self, value):
        raise NotImplementedError

    def getHeadAngleHorizontal(self):
        raise NotImplementedError

    def getHeadAngleVertikal(self):
        raise NotImplementedError

    def turnHeadHorizontal(self, value):
        raise NotImplementedError

    def turnHeadVertical(self, value):
        raise NotImplementedError

    def toggleLightInfrared(self):
        raise NotImplementedError

    def toggleLightVisible(self):
        raise NotImplementedError

    def setLightInfrared(self, status):
        raise NotImplementedError

    def setLightVisible(self, status):
        raise NotImplementedError

    def getLightInfrared(self):
        raise NotImplementedError

    def getLightVisible(self):
       raise NotImplementedError

    def captureImageRight(self):
        raise NotImplementedError

    def captureImageLeft(self):
        raise NotImplementedError

    def imageRightAvailable(self):
        raise NotImplementedError

    def imageLeftAvailable(self):
        raise NotImplementedError

    def getImageRight(self):
        raise NotImplementedError

    def getImageLeft(self):
        raise NotImplementedError
