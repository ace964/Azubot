import threading
import time
from camera import Camera

# Global variables for buffering images.
left_img_buffer = [b"",b""]
right_img_buffer = [b"",b""]
left_img_index = [0]
right_img_index = [0]

# Conditional objects for notifying clients.
left_img_cond = threading.Condition()
right_img_cond = threading.Condition()

RIGHT_CAMERA = Camera("21656532")
LEFT_CAMERA = Camera("21656530")

#global variables for fps_buffer counter
fps_buffer = [b"data:0.0\n\n", b"data:0.0\n\n"]
fps_index = [0]
fps_cond = threading.Condition()

class ImageProducer(threading.Thread):
    
    def __init__(self, queue, cond):
        self.queue = queue
        self.cond = cond
        
        threading.Thread.__init__(self)
        
    def start(self):
        """
        Starts the Thread
        """
        self.running = True
        super().start()
    
    def stop(self):
        """
        Stops the thread at the next possible "save" state
        """
        self.running = False
        
    def run(self):
        """
        Grab Thread grabs images from both cameras sequentially and converts them to compressed jpg.
        It then notifies all listening clients that the images have been updated.
        This has to happen sequentially because the RPi USB Controller cant handle the throughput of both at the same time.
        """
        global LEFT_CAMERA
        global left_img_cond
        global left_img_buffer
        global left_img_index
        
        global RIGHT_CAMERA
        global right_img_cond
        global right_img_buffer
        global right_img_index
        
        global fps_buffer
        
        while self.running:
		
            #time at frame begin. Used for fps_buffer calculation
            begin_frame = time.time()
            
            #capture frames
            self.__update_image(LEFT_CAMERA, left_img_buffer, left_img_index, left_img_cond)
            self.__update_image(RIGHT_CAMERA, right_img_buffer, right_img_index, right_img_cond)
            #print("Images Grabbed")
            #calculate fps_buffer
            self.__update_fps(begin_frame)
            time.sleep(0.01)
            
        #Close cameras when thread stops       
        if(LEFT_CAMERA is not None):   
            LEFT_CAMERA.Close()
            
        if(RIGHT_CAMERA is not None):   
            RIGHT_CAMERA.Close()
            
    
    def __update_fps(self, begin_frame):
        global fps_buffer
        global fps_index
        global fps_cond
        time_of_frame = time.time() - begin_frame
        self.queue.put(("data:f"+str(round(10 / time_of_frame)/10)+"\n\n").encode())
         
        with self.cond:
           self.cond.notifyAll()
    
    def __update_image(self, camera, buffer, index, cond):
        if(camera.IsOpen()):
            img = camera.GrabOne()
            
            buffer[(index[0] + 1) % 2] = (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + img + b'\r\n')
            index[0] = (index[0] + 1) % 2
            with cond:
                cond.notifyAll()
