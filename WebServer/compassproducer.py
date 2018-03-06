import smbus
import time
import math
import threading

#Kompass Sensor
class HMC5883L:
    
    #Attributvariablen
    __address = 0x1E
    __regx = 0x03
    __regy = 0x05
    __regz = 0x07
    __modeRegister = 0x02
    
    #Konstruktor
    def __init__(self, bus):
        self.cBus = bus
        self.__set_continous_measurement()
    
    #Methoden
    def __read_hword(self, reg):
        h = self.cBus.read_byte_data(self.__address, reg)
        l = self.cBus.read_byte_data(self.__address, reg+1)
        value = (h << 8) + l
        
        if (value >= 0x8000):
            return -((65535 - value) + 1)
        else:
            return value
    
    def get_heading(self):
        """
        Returns the magnetic field in 2D space as an angle.
        """
        x = self.__read_hword(self.__regx)
        y = self.__read_hword(self.__regy)
        z = self.__read_hword(self.__regz)
        
        heading = math.atan2(y,z) / (2*math.pi)*360 + 90   #+90, wegen der Ausrichtgung 
        
        if heading<0:
            heading = heading + 360
            
        return heading 
    
    def __set_continous_measurement(self):
        #ModeResgister auf 0 setzen (continuous measurement)
        self.cBus.write_byte_data(self.__address, self.__modeRegister, 0) #in Methode oder Konstruktor?
  
class CompassProducer(threading.Thread):

    def __init__(self, queue, cond):
        """
        Initializes Producer and Opens Sensor.
        """
        self.queue = queue
        self.cond = cond
        
        self.compass = HMC5883L(smbus.SMBus(1))
        
        threading.Thread.__init__(self)
        
    def start(self):
        """
        Overriden super().start()
        """
        self.running = True
        super().start()
    
    def stop(self):
        """
        Stops the Thread in the next possible "save" state
        """
        self.running = False
     
    def run(self):
        """
        Method is called when the Thread starts.
        Polls Sensor Data and puts it in queue every 0.1 Second.
        """
        while self.running:
            self.queue.put(("data:a"+str(int(self.compass.get_heading()))+"\n\n").encode())
            with self.cond:
                self.cond.notifyAll()
            time.sleep(0.2)
    
