import numpy as np
from azubot_gpio import *
import socket
from threading import Thread
import time

class AzubotMotorController:
    """Representation of a drive motor in the Azubot.

    An L293D H-Bridge Motor controller is used. For each motor, there
    are two enable-signals to choose the direction and one pwm speed
    control signal.

    The interface consists of the constructor and a method to set
    the motor speed. The motor speed is represented by a number between
    -100 (full reverse) and 100 (full forward), where 0 means halt.

    Methods:
    __init__(pin_enable_fw, pin_enable_rv, pwm)
    setSpeed(speed)
    """

    _speed_max = 100
    _speed_min = -100

    def __init__(self, pin_enable_fw, pin_enable_rv, pwm):
        """Constructor for a drive motor. The motor speed is set to 0.

        pin_enable_fw and pin_enable_rv have to implement the interface
        IPin, pwm has to implement the interface IPwm.
        """
        self.pin_enable_fw = pin_enable_fw
        self.pin_enable_rv = pin_enable_rv
        self.pwm = pwm
        self.setSpeed(0)

    def setSpeed(self, speed):
        """Set the speed of the motor.

        speed has to be within the bounds defined by the class.
        The motor will stop otherwise and an erro will be raised.
        """
        if 0 < speed <= self._speed_max:
            self.pin_enable_fw.write(1)
            self.pin_enable_rv.write(0)
            self.pwm.start(speed)
        elif 0 > speed >= self._speed_min:
            self.pin_enable_fw.write(0)
            self.pin_enable_rv.write(1)
            self.pwm.start(-speed)
        else:
            self.pwm.stop()
            self.pin_enable_fw.write(0)
            self.pin_enable_rv.write(0)
            if speed != 0:
                raise ValueError("speed value must be between ",self._speed_min," and ",self._speed_max)

class AzubotServoController:
    """Representation of a servo in the Azubot.

    The interface consists of the constructur and a method to set the
    angle of the servo. An angle of 0 means middle position, and angles
    <0 or >0 mean deviations from this position to either direction.

    Methods:
     __init__(pin)
     setAngle(angle)
    """

    angle_max = 30

    def __init__(self, pin):
        """Constructor for a servo. The servo is set to middle position.

        pin has to implement the interface IServo.
        """
        self.pin = pin
        self.pin.setAngle(0)

    def setAngle(self, percent):
        """Set the position of the servo.

        If the angle is outside of the allowed range, the servo keep its
        current position.
        """
        if abs(percent) <= 100:
            self.pin.setAngle(percent*self.angle_max/100)
    def reset(self):
        self.pin.reset()

class AzubotController(IAzubot):
    """Representation of the Basler Azubot.

    The Basler Azubot is a vehicle with chain drive and a movable camera
    head carrying two Basler dart cameras (one color, one b/w and IR
    sensitive) as well as white and IR-illumination. The head can be
    rotated and tilted.

    It utilizes a Raspberry Pi, which is running pigpio.
    Pigpio is a library, which launches a server listening on port 8887
    and handles all requests for hardware access of the raspberry pi.
    This Class uses the azubot_gpio class to process control signals.
 
    Another Task of this class, is to send hardware events to the
    Webserver (via socket), so information about battery status, light status and 
    other events can be displayed.
    """

    
    def __init__(self):
        

        # Connect to the local webserver socket, for data exchange
        self.conn = None
        serverConnect = Thread(target = self.connectToServer)
        serverConnect.start()
        
        # Initialize hardware from azubt_gpio.py
        self.IRLED     = IOAccess(4,IOAccess.OUTPUT)

        self.LED       = IOAccess(17,IOAccess.OUTPUT)

        self.PWM_RP_M1 = PWMAccess(26)

        self.TTL_RP_M11= IOAccess(22,IOAccess.OUTPUT)

        self.TTL_RP_M12= IOAccess(5,IOAccess.OUTPUT)

        self.PWM_RP_M2 = PWMAccess(27)

        self.TTL_RP_M21= IOAccess(6,IOAccess.OUTPUT)

        self.TTL_RP_M22= IOAccess(25,IOAccess.OUTPUT)

        self.SERVO_ROTATION= ServoAccess(19,minAngle=-60,maxAngle=50,minPulsewidth=500,midPulsewidth=1580,maxPulsewidth=2500)

        self.SERVO_TILT= ServoAccess(18,minAngle=-60,maxAngle=60,minPulsewidth=1000,midPulsewidth=1500,maxPulsewidth=2000)

        self.STATUS_S  = IOAccess(23,IOAccess.INPUT)

        self.STATUS_LED= IOAccess(24,IOAccess.OUTPUT)

        self.SOUND_PLAYER = SoundPlayer()
        
        # Initialize Motors and stop them
        self.motorLeft = AzubotMotorController(self.TTL_RP_M11, self.TTL_RP_M12, self.PWM_RP_M1)
        self.motorRight = AzubotMotorController(self.TTL_RP_M21, self.TTL_RP_M22, self.PWM_RP_M2)
        self.motorLeft.setSpeed(0)
        self.motorRight.setSpeed(0)

        # Initialize Servos and center them
        self.headRotationServo = AzubotServoController(self.SERVO_ROTATION)
        self.headRotationServo.setAngle(0)

        self.headTiltingServo = AzubotServoController(self.SERVO_TILT)
        self.headTiltingServo.setAngle(0)
        
        # Turn on LED on Motor Control Board.
        self.STATUS_LED.write(1)
        self.sendData(b"cON")

    ### Drive
    # To support drive control via thumbsticks as well as the triggers
    # of a gamepad, the interface allows to set the absolute speed and
    # the norm of the speed without changing its direction.
    # So when using the triggers (which give only positive values), use
    # the set(Left|Right)SpeedNorm and inverse(Left|Right)Speed methods,
    # when using the thumbsticks use only set(Left|Right)Speed methods.
    # At the moment, the factors are meant to be either 1 or -1, but
    # scaling might be a future functionality for the Azubot.
    leftSpeed = 0
    leftSpeedFactor = 1
    rightSpeed = 0
    rightSpeedFactor = 1

    def setLeftSpeed(self, percent):
        self.leftSpeed = percent
        self.leftSpeedFactor = 1
        self.motorLeft.setSpeed(self.getLeftSpeed())

    def setRightSpeed(self, percent):
        self.rightSpeed = percent
        self.rightSpeedFactor = 1
        self.motorRight.setSpeed(self.getRightSpeed())

    def setLeftSpeedNorm(self, percent):
        self.leftSpeed = percent
        self.motorLeft.setSpeed(self.getLeftSpeed())

    def setRightSpeedNorm(self, percent):
        self.rightSpeed = percent
        self.motorRight.setSpeed(self.getRightSpeed())

    def inverseLeftSpeed(self):
        self.leftSpeedFactor = -self.leftSpeedFactor
        self.motorLeft.setSpeed(self.getLeftSpeed())

    def inverseRightSpeed(self):
        self.rightSpeedFactor = -self.rightSpeedFactor
        self.motorRight.setSpeed(self.getRightSpeed())

    def getLeftSpeed(self):
        return self.leftSpeedFactor * self.leftSpeed

    def getRightSpeed(self):
        return self.rightSpeedFactor * self.rightSpeed

    ### Camera head
    headAngleHorizontal = 0
    headAngleVertical = 0
    lightInfrared = False
    lightVisible = False
    
    # Resets the head position
    def resetHeadPosition(self):
        self.sendData(b"h0")
        self.headRotationServo.reset()
        self.headTiltingServo.reset()
        
    # Sets a new head angle    
    def setHeadAngleHorizontal(self, percent):
        self.headAngleHorizontal = percent
        self.sendData(("h"+str(int(percent))).encode())
        self.headRotationServo.setAngle(-self.getHeadAngleHorizontal())

    # Sets a new head angle    
    def setHeadAngleVertical(self, percent):
        self.headAngleVertical = percent
        self.headTiltingServo.setAngle(-self.getHeadAngleVertical())

    # Get current head angle
    def getHeadAngleHorizontal(self):
        return self.headAngleHorizontal

    # Get current head angle
    def getHeadAngleVertical(self):
        return self.headAngleVertical

    # Add to angle position
    def turnHeadHorizontal(self, percent):
        self.setHeadAngleHorizontal(self.getHeadAngleHorizontal()+percent)

    # Add to angle position
    def turnHeadVertical(self, percent):
        self.setHeadAngleVertical(self.getHeadAngleVertical()+percent)

    # Toggle infrared (invisible) light mounted to head
    def toggleLightInfrared(self):
        self.setLightInfrared(not self.lightInfrared)

    # Toggle (visible) light mounted to head
    def toggleLightVisible(self):
        self.setLightVisible(not self.lightVisible)

    # Set infrared (invisible) light to certain state
    def setLightInfrared(self, status):
        self.IRLED.write(1 if status else 0)
        if(status):
            self.sendData(b"iON")
        else:
            self.sendData(b"iOFF")
            
        self.lightInfrared = status

    # Set light (visible) to certain state
    def setLightVisible(self, status):
        self.LED.write(1 if status else 0)
        
        if(status):
            self.sendData(b"vON")
        else:
            self.sendData(b"vOFF")
            
        self.lightVisible = status
    
    def getLightInfrared(self):
        return self.lightInfrared

    def getLightVisible(self):
        return self.lightVisible
    
    def playSound(self, filename): # plays sound in /home/pi/sounds/ + filename
        self.SOUND_PLAYER.play(filename)
    
    # Send data to webserver via socket connection.
    def sendData(self, data):
        if(self.conn is not None):
            self.conn.sendall(data)
    
    # Connect to the local socket for communication with the webserver
    def connectToServer(self):
        HOST = 'localhost'
        PORT = 54123
        while True:
            time.sleep(1)
            if(self.conn is None):
                conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    conn.connect((HOST, PORT))
                except BaseException:
                    continue
                self.conn = conn  
   