import numpy as np
import cv2
import os
import re

from io.handlers.frame_ouput_handler import FrameOutputHandler

class RingBuffer:
    def __init__(self, size, output_path, frame_width, frame_height):
        self.data = np.zeros(size, dtype=np.uint8)
        self.index = 0
        self.size = size
        # adjust frame size
        if frame_width == 0 or frame_height == 0:
            self.frame_size = (640, 480)
        else:
            self.frame_size = (frame_width, frame_height)
        self.output_path = output_path

    def append(self, x):
        self.data[self.index] = x
        self.index = (self.index + 1) % self.size
        if self.index == 0:
            self.dump_to_disk()

    def dump_to_disk(self):        
        handler = FrameOutputHandler(output_path=self.output_path)
        if 'CONFIGURATION_NAME' in os.environ:
            configuration_name = os.environ['CONFIGURATION_NAME']
            dev_node = re.compile(configuration_name + "-[\da-f]{6}-svc")           
        elif 'VIDEO_PATH' in os.environ:    
            dev_node = os.environ['VIDEO_PATH']        
        
        out = cv2.VideoWriter(handler.get_output_path(dev_node), cv2.VideoWriter_fourcc(*'mp4v'), 20.0, self.frame_size)
        for frame in self.data:
            out.write(frame)
        out.release()