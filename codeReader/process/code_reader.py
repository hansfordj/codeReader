from imutils.video import VideoStream
from pyzbar import pyzbar
import datetime
import imutils
import time
import cv2


class Camera():
    __initialized = False
    def __init__(self):
        self.release = False
        if Camera.__initialized:
            raise Exception("You can't create more than 1 instance of Camera")
        Camera.__initialized = True

    def triggerScan(self):
        print("[INFO]  STARTING VIDEO STREAM...")
        if not self.release:
            self.vs = VideoStream(usePiCamera=True).start()  # Prepare the camera...
        
        print("Camera warming up ...")
        time.sleep(2.0)

        # loop over the frames from the video stream
        while True:
            # grab the frame from the threaded video stream and resize it to
            # have a maximum width of 600 pixels
            print("[INFO]  CAPTURING FRAME...")
            frame = self.vs.read()
            frame = imutils.resize(frame, width=600)
            print("[INFO]  WRITING TEMP PRE-PROCESSED FRAME")
            cv2.imwrite("pre-output.jpg", frame)
            time.sleep(0.5)
            
         
            # find the codes in the frame and decode each of the codes
            print("[INFO]  CHECKING FOR CODES")
            codes = pyzbar.decode(frame)
                # loop over the detected code
            if not codes:
                print("[INFO]  NO CODES")
                
            for code in codes:
            
                # extract the bounding box location of the code and draw
                # the bounding box surrounding the code on the image
                (x, y, w, h) = code.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
         
                # the code data is a bytes object so if we want to draw it
                # on our output image we need to convert it to a string first
                codeData = code.data.decode("utf-8")
                codeType = code.type
                
                if codeData:
                
                    
                    print("Code:{}".format(codeData))
                    time.sleep(.2)
                    print("[INFO] cleaning up...")
                    self.vs.stop()
         
                    # draw the code data and code type on the image
                    text = "{} ({})".format(codeData, codeType)
                    cv2.putText(frame, text, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
             
                
                    cv2.imwrite("outputtest.jpg", frame)
                    
                    return {'codeData': codeData, 'codeType': codeType}
         
            # if the `q` key was pressed, break from the loop
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if self.release == True:
                
                break
        print("[INFO] CAMERA RELEASED. CLEANING UP...")
        self.vs.stop()
        time.sleep(1)
        print("[INFO] CAMERA STREAM STOPPED.")
        
    
    
    def release_camera(self):
        print("[INFO]  CAMERA RELEASE REQUESTED...")
        self.release = True 

    def enable_camera(self):
        if self.release == True:
            self.release = False
        return True

if __name__ == "__main__":

    codeStart()

