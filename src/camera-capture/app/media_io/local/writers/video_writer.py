import json

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

    def _write_file(self, path: str, data):
        """
        Writes the given data to a video format file.

        Args:
            path (str): The path to the video format file.
            data: The data to be written to the file.

        Returns:
            None

        """
        with open(path, "a") as file:
            file.write(data)
