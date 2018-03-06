import socket
import threading

class SocketProducer(threading.Thread):

    running = False
    
    def __init__(self, queue, cond):
        self.queue = queue
        self.cond = cond
        
        threading.Thread.__init__(self)
        
        
    def run(self):
        """
        Called when thread starts.
        Opens a socket on port 54321 and listens to connected clients.
        """
        HOST = 'localhost'        # Symbolic name meaning all available interfaces
        PORT = 54123              # Arbitrary non-privileged port
       
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            while(self.running):
                s.listen(1)
                conn, addr = s.accept()
                self.listen_to_connection(conn)
                conn.close()
            s.close()
                
    def is_running(self):
        """
        Returns if the thread is running
        """
        return self.running
        
    def start(self):
        """
        Starts the thread
        """
        self.running = True
        super().start()
        
    def stop(self):
        """
        Stops the thread at the next possible "save" state
        """
        self.running = False
        
    def __update(self, data):

        self.queue.put( b"data:" + data + b"\n\n")
       
        with self.cond:
            self.cond.notifyAll()
            
    def listen_to_connection(self, conn):
        """
        Listens to the given connection conn and puts the recived data into queue
        """
        with conn:
            print("Connected")
            while self.running:
                data = conn.recv(32)
                if not data: 
                   return
                   
                print("Recived Data:"+str(data))
                self.__update(data)