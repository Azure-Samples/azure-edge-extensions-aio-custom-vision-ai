import sys
import os

from globals import global_stop_event
from time import sleep
import grpc

import camera_pb2
import camera_pb2_grpc

from flask import Flask, render_template, Response

import threading
import logging
from concurrent import futures
import queue
import traceback

class CameraFeed:
    def __init__(self, url):
        global global_stop_event

        self.url = url
        self.queue = queue.Queue(1)
        self.thread = None
        self.stop_event = global_stop_event

    def __eq__(self, other):
        if other is None:
            return False
        return self.url == other.url

    def start_handler(self):
        self.thread = threading.Thread(target=self.get_frames)
        self.thread.start()

    def wait_handler(self):
        if self.thread is not None:
            self.thread.join()

    # Generator function for video streaming.
    def generator_func(self):
        while not self.stop_event.wait(0.01):
            frame = self.queue.get(True, None)
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    # Loops, creating gRPC client and grabing frame from camera serving specified url.
    def get_frames(self):
        logging.info("Starting get_frames(%s)" % self.url)
        while not self.stop_event.wait(0.01):
            try:
                client_channel = grpc.insecure_channel(self.url, options=(
                    ('grpc.use_local_subchannel_pool', 1),))
                camera_stub = camera_pb2_grpc.CameraStub(client_channel)
                frame = camera_stub.GetFrame(camera_pb2.NotifyRequest())
                frame = frame.frame
                client_channel.close()

                frame_received = False
                # prevent stale data
                if (len(frame) > 0):
                    if (self.queue.full()):
                        try:
                            self.queue.get(False)
                        except:
                            pass
                    self.queue.put(frame, False)
                    frame_received = True
                
                if (frame_received):
                    sleep(1)

            except:
                logging.info("[%s] Exception %s" % (self.url, traceback.format_exc()))
                sleep(1)
    """
    This function returns the raw frame data received from the gRPC server.
    If the frame data is empty or an exception occurs, it will continue to the next iteration of the loop after a 1-second delay.
    """    
    def get_raw_frame(self):
        logging.info("Starting get_raw_frame(%s)" % self.url)
        while not self.stop_event.wait(0.01):
            try:
                client_channel = grpc.insecure_channel(self.url, options=(('grpc.use_local_subchannel_pool', 1),))
                camera_stub = camera_pb2_grpc.CameraStub(client_channel)
                frame = camera_stub.GetFrame(camera_pb2.NotifyRequest())
                frame = frame.frame
                client_channel.close()

                if len(frame) > 0:
                    return frame   

            except:
                logging.info("[%s] Exception %s" % (self.url, traceback.format_exc()))
                sleep(1)                             

class CameraDisplay:
    def __init__(self):
        self.main_camera = None
        self.small_cameras = []
        self.mutex = threading.Lock()

    def __eq__(self, other):
        return self.main_camera == other.main_camera and self.small_cameras == other.small_cameras
        
    def start(self):
        if self.main_camera is not None:
            self.main_camera.start_handler()
        for small_camera in self.small_cameras:
            small_camera.start_handler()

    def wait_handlers(self):
        global global_stop_event

        global_stop_event.set()
        if self.main_camera is not None:
            self.main_camera.wait_handler()
        for small_camera in self.small_cameras:
            small_camera.wait_handler()
        global_stop_event.clear()
        
    def merge(self, other):
        self.mutex.acquire()
        try:
            self.wait_handlers()

            self.main_camera = other.main_camera
            self.small_cameras = other.small_cameras

            self.start_handlers()
        finally:
            self.mutex.release()

    def count(self):
        self.mutex.acquire()    
        result = len(self.small_cameras)
        if self.main_camera is not None:
            result += 1
        self.mutex.release()
        return result

    def hash_code(self):
        self.mutex.acquire()
        cameras = ",".join([camera.url for camera in self.small_cameras])
        if self.main_camera is not None:
            cameras = "{0}+{1}".format(self.main_camera.url, cameras)
        self.mutex.release()
        return cameras

    def stream_frames(self, camera_id=0):
        selected_camera = None
        camera_id = int(camera_id)

        self.mutex.acquire()
        if camera_id == 0:
            selected_camera = self.main_camera
        elif camera_id - 1 < len(self.small_cameras):
            selected_camera = self.small_cameras[camera_id - 1]
        self.mutex.release()
        
        if selected_camera is None:
            return Response(None, 500)
        else:
            return Response(selected_camera.generator_func(), mimetype='multipart/x-mixed-replace; boundary=frame')
        
    def read(self, camera_id=0):
        selected_camera = None
        camera_id = int(camera_id)

        self.mutex.acquire()
        if camera_id == 0:
            selected_camera = self.main_camera
        elif camera_id - 1 < len(self.small_cameras):
            selected_camera = self.small_cameras[camera_id - 1]
        self.mutex.release()
        
        if selected_camera is None:
            return None
        else:
            return selected_camera.get_raw_frame()        
