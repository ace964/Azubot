from flask import Flask, render_template, Response, request, redirect, url_for

from imageproducer import *
from periodicproducer import PeriodicProducer
from socketproducer import SocketProducer
from compassproducer import CompassProducer
import os.path
import os
import time
import subprocess
from queue import Queue

app = Flask(__name__)

queue = Queue()
cond = threading.Condition()

img_prod = None
per_prod = None
soc_prod = None
com_prod = None


def shutdown():
    """
    Raises a RuntimeError to shutdown the server and the Pi
    """
    raise RuntimeError("Server going down")


def client(buffer, index, cond):
    """
    Client function for yielding data from buffer.
    """
    yield buffer[index[0]]
    while True:
        with cond:
            cond.wait()
            
        yield buffer[index[0]]
        
@app.before_first_request
def setup():
    """
    Setup function for initializing cameras and starting Producer Threads.
    """
    if(not RIGHT_CAMERA.IsOpen()):
        RIGHT_CAMERA.Open()
        
    if(not LEFT_CAMERA.IsOpen()):
        LEFT_CAMERA.Open()
    global img_prod
    global per_prod
    global soc_prod
    global com_prod
    img_prod = ImageProducer(queue, cond)
    per_prod = PeriodicProducer(queue, cond)
    soc_prod = SocketProducer(queue, cond)
    com_prod = CompassProducer(queue, cond)
    img_prod.start()
    per_prod.start()
    soc_prod.start()
    com_prod.start()

def status_client():
    """
    Yields the content of the queue when cond is notified
    """
    global cond
    global queue
    
    while True:
        with cond:
            cond.wait()
            
        while not queue.empty():
            yield queue.get()
        
@app.route('/')
def index():
    """
    Video streaming home page.
    """
    return render_template('index.html')

        
@app.route('/status')
def status():
    """
    Text event-stream for all status updates.
    """
    return Response(status_client(), content_type='text/event-stream', status=200)

@app.route('/video_feed_right')
def video_feed_right():
    """
    The response for the right image
    """
    global right_img_cond
    global right_img_buffer
    global right_img_index
    return Response(client(right_img_buffer, right_img_index, right_img_cond), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_left')
def video_feed_left():
    """
    The Response for the left image
    """
    global left_img_cond
    global left_img_buffer
    global left_img_index
    return Response(client(left_img_buffer, left_img_index, left_img_cond), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port =80, threaded=True)
    except RuntimeError:
        subprocess.call("sudo shutdown -hP now", shell=True)
        
    if(img_prod is not None):
        img_prod.stop()
        img_prod.join()
        
    if(per_prod is not None):
        per_prod.stop()
        per_prod.join()
        
    if(com_prod is not None):
        com_prod.stop()
        com_prod.join()  
        
    if(soc_prod is not None):
        soc_prod.stop()
        soc_prod.join()