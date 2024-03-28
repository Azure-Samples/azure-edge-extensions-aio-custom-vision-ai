from media_io.handlers.media_handler import MediaHandler
from media_io.handlers.typing import T, U
from media_io.local.writers.video_writer import VideoWriter
from media_io.local.loaders.video_loader import VideoLoader

import cv2


class FrameOutputHandler(MediaHandler):
    """
    A class that handles frame outputs for a given video capture.
    """

    def __init__(
        self, data_location: str, writer: T = VideoWriter(), loader: U = VideoLoader()
    ) -> None:
        """
        Initializes a FrameOutputHandler instance.

        Args:
            data_location (str): The location where the data is stored.
        """
        super().__init__(data_location=data_location, writer=writer, loader=loader)

    def _get_output_name(self, frame_index_name: str, extension: str = ".avi") -> str:
        """
        Returns the output name for a given video capture.

        Args:
            frame_index_name (str): The name of the index.
            extension (str): The file extension for the output file.

        Returns:
            str: The output name.
        """
        return f"frame_index_{frame_index_name}{extension}"

    def get_output_path(self, frame_index_name: str, extension: str = ".avi") -> str:
        """
        Returns the output path for a given video capture.

        Args:
            frame_index_name (str): The name of the index.
            extension (str): The file extension for the output file.

        Returns:
            str: The output path.

        Raises:
            ValueError: If the provided extension is not a valid video file extension.
        """
        valid_extensions = [".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv"]
        if extension not in valid_extensions:
            raise ValueError(f"Invalid video file extension: {extension}. Valid extensions are {valid_extensions}.")

        return f"{self.data_location}/{self._get_output_name(frame_index_name, extension)}"

    def handle_archive_by_index(self, frame_index_name: str) -> str | None:
        """
        Handles archiving of frame output for a given video capture.

        Args:
            frame_index_name (str): The name of the index.

        Returns:
            str | None: The output filename if successful, None otherwise.
        """
        output_filename = self._get_output_name(frame_index_name)
        return self.handle_archive(output_filename)
    
    def save(self, data: cv2.VideoWriter, index_name: str):
        """
        Saves the query output for a given index name.

        Args:
            data (FrameOutput): The query output to be saved.
            index_name (str): The name of the index.
        """
        output_filename = self._get_output_name(index_name)
        self.save_dict(data.__dict__, output_filename)

