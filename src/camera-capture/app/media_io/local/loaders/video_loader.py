import sys
if sys.version_info[0] < 3:#e.g python version <3
    import cv2
else:
    import cv2

from media_io.local.loaders.local_loader import LocalLoader

class VideoLoader(LocalLoader):
    """A class for loading data from video media files."""

    def load(self, path: str) -> list:
        """Load data from a video media file.

        Args:
            path (str): The path to the video media file.

        Returns:
            list: A list of loaded frames.

        Raises:
            FileNotFoundError: If the file is not found at the specified path.
        """
        if not self.exists(path):
            raise FileNotFoundError(f"File not found at path: {path}")

        # Open the video file
        cap = cv2.VideoCapture(path)

        frames = []
        while True:
            # Read a frame
            ret, frame = cap.read()

            # If the frame was not successfully read, then we have reached the end of the video
            if not ret:
                break

            # Append the frame to the list
            frames.append(frame)

        # Release the VideoCapture object
        cap.release()

        return frames

    def can_handle(self, path: str) -> bool:
        """Check if the loader can handle the given file path.

        Args:
            path (str): The file path to check.

        Returns:
            bool: True if the loader can handle the file, False otherwise.
        """
        valid_extensions = [".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv"]
        ext = self._get_file_ext(path)
        return ext in valid_extensions
