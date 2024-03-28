import numpy as np
import cv2

from media_io.handlers.frame_ouput_handler import FrameOutputHandler

class RingBuffer:
    def __init__(self, size, output_path, identifier, frame_width, frame_height):
        self.data = [None]*size  # Initialize with None
        self.index = 0
        self.buffer_cnt = 0
        self.size = size
        self.identifier = identifier
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
        self.buffer_cnt=self.buffer_cnt+1 
        frame_index_name = self.identifier + "_" + str(self.buffer_cnt)      
        print("Dumping data to disk. output path: {0}, frame_index_name: {1}".format(self.output_path, frame_index_name))
        handler = FrameOutputHandler(data_location=self.output_path, frame_rate=20.0, frame_size=self.frame_size)       
        handler.handle_archive_by_index(frame_index_name=frame_index_name)
        handler.save(self.data, frame_index_name=frame_index_name)
