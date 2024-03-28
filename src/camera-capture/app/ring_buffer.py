import numpy as np
import cv2

from media_io.handlers.frame_ouput_handler import FrameOutputHandler

class RingBuffer:
    def __init__(self, size, output_path, identifier, frame_width, frame_height):
        self.data = [None]*size  # Initialize with None
        self.index = 0
        self.size = size
        self.identifier = identifier
        # adjust frame size
        if frame_width == 0 or frame_height == 0:
            self.frame_size = (640, 480)
        else:
            self.frame_size = (frame_width, frame_height)
        self.output_path = output_path

    def append(self, x):
        print
        self.data[self.index] = x
        self.index = (self.index + 1) % self.size
        if self.index == 0:
            self.dump_to_disk()

    def dump_to_disk(self):        
        handler = FrameOutputHandler(data_location=self.output_path)       
        print("Dumping data to disk. output path: ", handler.get_output_path(frame_index_name=self.identifier, extension=".mp4"))
        out = cv2.VideoWriter(handler.get_output_path(frame_index_name=self.identifier,extension=".mp4"), cv2.VideoWriter_fourcc(*'mp4v'), 20.0, self.frame_size)
        handler.save
        for frame in self.data:
            print("Writing frame to disk")
            out.write(frame)
        out.release()