#To make python 2 and python 3 compatible code
from __future__ import division
from __future__ import absolute_import

#Imports
import sys
if sys.version_info[0] < 3:#e.g python version <3
    import cv2
else:
    import cv2
# pylint: disable=E1101
# pylint: disable=E0401
# Disabling linting that is not supported by Pylint for C extensions such as OpenCV. See issue https://github.com/PyCQA/pylint/issues/1955 
import numpy as np
import requests
import json
import time

import video_stream
from video_stream import VideoStream
import annotation_parser
from annotation_parser import AnnotationParser
import image_server
from image_server import ImageServer
from grpc_video_stream import CameraFeed, CameraDisplay
import threading
from globals import global_stop_event
from ring_buffer import RingBuffer

# global counters
BUFFER_SIZE = 100

class CameraCapture(object):

    def __IsInt(self,string):
        try: 
            int(string)
            return True
        except ValueError:
            return False

    def __init__(
            self,
            videoPath,
            videoUrl = "",
            imageProcessingEndpoint = "",
            imageProcessingParams = "", 
            showVideo = False, 
            verbose = False,
            loopVideo = True,
            convertToGray = False,
            resizeWidth = 0,
            resizeHeight = 0,
            annotate = False,
            sendToPubSubCallback = None):
        self.isOtherCam = False
        self.isWebcam = False
        self.isVideoFile = False
        self.videoPath = videoPath
        self.blob_dir = f"/mnt/blob"       
        if (videoUrl != ""):
            self.videoUrl = videoUrl         
            self.isOtherCam = True
            self.capture_identifier = videoUrl.replace(".", "-").replace(":", "_")
        else:
            self.capture_identifier = videoPath.replace("/", "-")
            if self.__IsInt(videoPath):
                #case of a usb camera (usually mounted at /dev/video* where * is an int)
                self.isWebcam = True
                
            else:
                #case of a video file
                self.isVideoFile = True
        self.imageProcessingEndpoint = imageProcessingEndpoint
        if imageProcessingParams == "":
            self.imageProcessingParams = "" 
        else:
            self.imageProcessingParams = json.loads(imageProcessingParams)
        self.showVideo = showVideo
        self.verbose = verbose
        self.loopVideo = loopVideo
        self.convertToGray = convertToGray
        self.resizeWidth = resizeWidth
        self.resizeHeight = resizeHeight
        self.annotate = (self.imageProcessingEndpoint != "") and self.showVideo & annotate
        self.nbOfPreprocessingSteps = 0
        self.autoRotate = False
        self.sendToPubSubCallback = sendToPubSubCallback
        self.vs = None
        self.capture = None
        # Iniiialise the buffer
        self.buffer = RingBuffer(
            BUFFER_SIZE, 
            output_path=self.blob_dir, 
            identifier=self.capture_identifier, 
            frame_width=resizeWidth, 
            frame_height=resizeHeight
        )

        if self.convertToGray:
            self.nbOfPreprocessingSteps +=1
        if self.resizeWidth != 0 or self.resizeHeight != 0:
            self.nbOfPreprocessingSteps +=1
        if self.verbose:
            print("Initialising the camera capture with the following parameters: ")
            print("   - Video path: " + self.videoPath)
            print("   - Video Url: " + self.videoUrl)
            print("   - Image processing endpoint: " + self.imageProcessingEndpoint)
            print("   - Image processing params: " + json.dumps(self.imageProcessingParams))
            print("   - Verbose: " + str(self.verbose))
            print("   - Show video: " + str(self.showVideo))
            print("   - Loop video: " + str(self.loopVideo))
            print("   - Convert to gray: " + str(self.convertToGray))
            print("   - Resize width: " + str(self.resizeWidth))
            print("   - Resize height: " + str(self.resizeHeight))
            print("   - Annotate: " + str(self.annotate))
            print("   - Send processing results to pubsub: " + str(self.sendToPubSubCallback is not None))
            print()
        
        self.displayFrame = None
        if self.showVideo:
            self.imageServer = ImageServer(5012, self)
            self.imageServer.start()

    def __annotate(self, frame, response):
        AnnotationParserInstance = AnnotationParser()
        #TODO: Make the choice of the service configurable
        listOfRectanglesToDisplay = AnnotationParserInstance.getCV2RectanglesFromProcessingService1(response)
        for rectangle in listOfRectanglesToDisplay:
            cv2.rectangle(frame, (rectangle(0), rectangle(1)), (rectangle(2), rectangle(3)), (0,0,255),4)
        return

    def __sendFrameForProcessing(self, frame):
        headers = {'Content-Type': 'application/octet-stream'}
        try:
            response = requests.post(self.imageProcessingEndpoint, headers = headers, params = self.imageProcessingParams, data = frame)
        except Exception as e:
            print('__sendFrameForProcessing Excpetion -' + str(e))
            return "[]"

        if self.verbose:
            try:
                print("Response from external processing service: (" + str(response.status_code) + ") " + json.dumps(response.json()))
            except Exception:
                print("Response from external processing service (status code): " + str(response.status_code))
        return json.dumps(response.json())

    def __displayTimeDifferenceInMs(self, endTime, startTime):
        return str(int((endTime-startTime) * 1000)) + " ms"

    def __enter__(self):
        if self.isOtherCam:            
            self.camera_display = CameraDisplay()
            self.camera_display.main_camera = CameraFeed(self.videoUrl) 
            self.camera_display.small_cameras.sort(key=lambda camera: camera.url)  
            self.vs = self.camera_display 
            #time.sleep(1.0)#needed to load at least one frame into the VideoStream class
        elif self.isWebcam:
            #The VideoStream class always gives us the latest frame from the webcam. It uses another thread to read the frames.
            self.vs = VideoStream(int(self.videoPath)).start()
            time.sleep(1.0)#needed to load at least one frame into the VideoStream class
            self.capture = cv2.VideoCapture(int(self.videoPath))
        else:
            #In the case of a video file, we want to analyze all the frames of the video thus are not using VideoStream class
            self.capture = cv2.VideoCapture(self.videoPath)
        return self    

    def get_display_frame(self):
        return self.displayFrame    

    def start(self):
        frameCounter = 0
        perfForOneFrameInMs = None
        while True:
            if self.showVideo or self.verbose:
                startOverall = time.time()
            if self.verbose:
                startCapture = time.time()

            frameCounter +=1
            if not self.isVideoFile:
                if self.vs is None:
                    raise Exception("self.vs is not initialized")                
                frame = self.vs.read()
                if (self.isOtherCam):
                    # assuming the frame data is raw bytes
                    frame = cv2.imdecode(np.frombuffer(frame, dtype=np.uint8), cv2.IMREAD_COLOR)  # decode the frame
            else:
                frame = self.capture.read()[1]
                if frameCounter == 1:
                    if self.capture.get(cv2.CAP_PROP_FRAME_WIDTH) < self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT):
                        self.autoRotate = True
                if self.autoRotate:
                    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE) #The counterclockwise is random...It coudl well be clockwise. Is there a way to auto detect it?
            if self.verbose:
                if frameCounter == 1:
                    if self.isVideoFile:
                        print("Original frame size: " + str(int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))) + "x" + str(int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))))
                        print("Frame rate (FPS): " + str(int(self.capture.get(cv2.CAP_PROP_FPS))))
                print("Frame number: " + str(frameCounter))
                print("Time to capture (+ straighten up) a frame: " + self.__displayTimeDifferenceInMs(time.time(), startCapture))
                startPreProcessing = time.time()
            
            #Loop video
            if self.isVideoFile:             
                if frameCounter == self.capture.get(cv2.CAP_PROP_FRAME_COUNT):
                    if self.loopVideo: 
                        frameCounter = 0
                        self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    else:
                        break

            #Pre-process locally
            if self.nbOfPreprocessingSteps == 1 and self.convertToGray:
                preprocessedFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if self.nbOfPreprocessingSteps == 1 and (self.resizeWidth != 0 or self.resizeHeight != 0):
                preprocessedFrame = cv2.resize(frame, (self.resizeWidth, self.resizeHeight))

            if self.nbOfPreprocessingSteps > 1:
                preprocessedFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                preprocessedFrame = cv2.resize(preprocessedFrame, (self.resizeWidth,self.resizeHeight))
            
            if self.verbose:
                print("Time to pre-process a frame: " + self.__displayTimeDifferenceInMs(time.time(), startPreProcessing))
                startEncodingForProcessing = time.time()

            #Process externally
            if self.imageProcessingEndpoint != "":

                #Encode frame to send over HTTP
                if self.nbOfPreprocessingSteps == 0:
                    #Push frame buffer
                    self.buffer.append(frame)  
                    encodedFrame = cv2.imencode(".jpg", frame)[1].tostring()
                else:
                    self.buffer.append(preprocessedFrame) 
                    encodedFrame = cv2.imencode(".jpg", preprocessedFrame)[1].tostring()

                if self.verbose:
                    print("Time to encode a frame for processing: " + self.__displayTimeDifferenceInMs(time.time(), startEncodingForProcessing))
                    startProcessingExternally = time.time()      

                #Send over HTTP for processing
                # response = self.__sendFrameForProcessing(encodedFrame)
                # if self.verbose:
                #     print("Time to process frame externally: " + self.__displayTimeDifferenceInMs(time.time(), startProcessingExternally))
                #     startSendingToPubSub = time.time()

                # #forwarding outcome of external processing to the pubsub
                # if response != "[]" and self.sendToPubSubCallback is not None:
                #     self.sendToPubSubCallback(response)
                #     if self.verbose:
                #         print("Time to message from processing service to pubsub: " + self.__displayTimeDifferenceInMs(time.time(), startSendingToPubSub))
                #         startDisplaying = time.time()

            #Display frames
            if self.showVideo:
                try:
                    if self.nbOfPreprocessingSteps == 0:
                        if self.verbose and (perfForOneFrameInMs is not None):
                            cv2.putText(frame, "FPS " + str(round(1000/perfForOneFrameInMs, 2)),(10, 35),cv2.FONT_HERSHEY_SIMPLEX,1.0,(0,0,255), 2)
                        if self.annotate:
                            #TODO: fix bug with annotate function
                            self.__annotate(frame, response)
                        self.displayFrame = cv2.imencode('.jpg', frame)[1].tobytes()
                    else:
                        if self.verbose and (perfForOneFrameInMs is not None):
                            cv2.putText(preprocessedFrame, "FPS " + str(round(1000/perfForOneFrameInMs, 2)),(10, 35),cv2.FONT_HERSHEY_SIMPLEX,1.0,(0,0,255), 2)
                        if self.annotate:
                            #TODO: fix bug with annotate function
                            self.__annotate(preprocessedFrame, response)
                        self.displayFrame = cv2.imencode('.jpg', preprocessedFrame)[1].tobytes()
                except Exception as e:
                    print("Could not display the video to a web browser.") 
                    print('Excpetion -' + str(e))
                if self.verbose:
                    if 'startDisplaying' in locals():
                        print("Time to display frame: " + self.__displayTimeDifferenceInMs(time.time(), startDisplaying))
                    elif 'startSendingToPubSub' in locals():
                        print("Time to display frame: " + self.__displayTimeDifferenceInMs(time.time(), startSendingToPubSub))
                    else:
                        print("Time to display frame: " + self.__displayTimeDifferenceInMs(time.time(), startEncodingForProcessing))
                perfForOneFrameInMs = int((time.time()-startOverall) * 1000)
                if self.isVideoFile:
                    waitTimeBetweenFrames = max(int(1000 / self.capture.get(cv2.CAP_PROP_FPS))-perfForOneFrameInMs, 1)
                    if self.verbose:
                        print("Wait time between frames :" + str(waitTimeBetweenFrames))
                    if cv2.waitKey(waitTimeBetweenFrames) & 0xFF == ord('q'):
                        break

            if self.verbose:
                perfForOneFrameInMs = int((time.time()-startOverall) * 1000)
                print("Total time for one frame: " + self.__displayTimeDifferenceInMs(time.time(), startOverall))

    def __exit__(self, exception_type, exception_value, traceback):
        if self.isVideoFile:
            if self.capture is None:
                raise Exception("self.capture is not initialized")            
            self.capture.release()
        if self.showVideo:
            self.imageServer.close()
            cv2.destroyAllWindows()