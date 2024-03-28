import cv2

from media_io.local.writers.local_writer import LocalWriter
from utils.logging import get_logger

logger = get_logger(__name__)


class VideoWriter(LocalWriter):
    """
    A class for writing data to a video file.

    Inherits from the LocalWriter class.

    Attributes:
        None

    Methods:
        write_file: Writes data to a video format file.

    """
    def __init__(self, fourcc: int = cv2.VideoWriter_fourcc(*"XVID"), fps: int = 30, frame_size: tuple = (640, 480)):
        """
        Initializes a VideoWriter instance.

        Args:
            fourcc (int): The four character code for the codec.
            fps (int): The frames per second.
            frame_size (tuple): The frame size.

        """
        self.fourcc = fourcc
        self.fps = fps
        self.frame_size = frame_size

    def _write_file(self, path: str, data):
        """
        Writes the given data to a video format file.

        Args:
            path (str): The path to the video format file.
            data: The data to be written to the file.

        Returns:
            None

        """
        out = cv2.VideoWriter(path, self.fourcc, self.fps, self.frame_size)
        with open(path, "a") as file:
            for frame in data:
                out.write(frame)
            out.release()                
