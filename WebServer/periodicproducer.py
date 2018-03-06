import threading
import pigpio
import subprocess
import re
import time

pins = pigpio.pi(port=8887)

class PeriodicProducer(threading.Thread):

    def __init__(self, queue, cond):
        """
        Initializes thread
        """
        self.queue = queue
        self.cond = cond
        
        threading.Thread.__init__(self)
        
    def start(self):
        """
        Starts thread
        """
        self.running = True
        super().start()
    
    def stop(self):
        """
        Stops thread at the next possible "save" state
        """
        self.running = False
     
    def run(self):
        """
        Called when thread starts.
        Checks battery state and signal quality every 5 seconds 
        put this information into queue
        """
        while self.running:
            self.__update_battery()
            self.__update_signal()
            time.sleep(5)
    
    def __update_signal(self):
        
        x = str(subprocess.check_output('sudo iwconfig  wlan0| grep -i quality', shell=True))
        qual = re.search("Link Quality=([0-9]*)/([0-9]*)", x)
        strength = int(qual.group(1))
        max = int(qual.group(2))
        q = (strength / max * 3)
        self.queue.put(("data:s"+str(int(q))+"\n\n").encode())

        with self.cond:
           self.cond.notifyAll()
        
    def __update_battery(self):
        global pins
        
        AKKU2_PIN = 21
        AKKU3_PIN = 20
        AKKU4_PIN = 16
        v_state = b""
        if(pins.read(AKKU4_PIN) == 1):
            v_state = b"data:bok\n\n"
        elif(pins.read(AKKU3_PIN) == 1):
            v_state = b"data:blow\n\n"
        elif(pins.read(AKKU2_PIN) == 1):
            v_state = b"data:bcrit\n\n"
        else:
            shutdown()
            
        self.queue.put(v_state)
        with self.cond:
           self.cond.notifyAll()
            