import cv2
import numpy as np
import pypylon.pylon as py
from time import sleep
from threading import Lock
#from PIL import Image

class Camera:
    """
    Camera wrapper for Basler camera.
    To work correctly the camera has to be able to set binning and use BayerGB8 PixelFormat
    Camera is thread save.
    """
    def __init__(self, serialNumber):
        """
        Initializes a Camera with the given serial number
        """
        self.cam = None
        self.serial = serialNumber
        device_info = py.DeviceInfo()
        device_info.SetSerialNumber(serialNumber)
        self.cam = py.InstantCamera(py.TlFactory.GetInstance().CreateDevice(device_info))
        self.lock = Lock()

    def Open(self):
        """
        Opens the camera and sets params.
        """
        self.lock.acquire()
            
        self.cam.Open()

        self.cam.BinningHorizontal.Value = 4
        self.cam.BinningVertical.Value = 4
        self.cam.Width.Value=270
        self.cam.Height.Value=270
        self.cam.PixelFormat.Value="BayerGB8"

        self.lock.release()

    def IsOpen(self):
        """
        Checks if the Camera is open
        """
        return self.cam.IsOpen()
        
    def Close(self):
        """
        Closes the Camera.
        """
        self.cam.Close()

    def GrabOne(self):
        """
        Grabs an image from the camera and converts it into a jpg string
        """
        self.lock.acquire()
            
        img = None
        with self.cam.GrabOne(1000) as grab_result:
            if grab_result.GrabSucceeded():
                img = grab_result.Array
        
        self.lock.release()
            
        if(img is None):
            return b""
        
        #imgNew = Image.fromarray(img)
        #imgrgb = Image.merge('RGB', (imgNew,imgNew,imgNew)) # color image
        #imgrgb.save('my.jpg')
        #return imgrgb.convert("RGB").tobytes("raw", "RGB")
        img = cv2.cvtColor(img, cv2.COLOR_BayerGB2RGB)
        img = np.rot90(img, 3)
        unused, imgEnc = cv2.imencode(".jpg",img)
        return imgEnc.tostring()


    def __del__(self):
        """
        destructor closes the Camera.
        """
        self.cam.Close()