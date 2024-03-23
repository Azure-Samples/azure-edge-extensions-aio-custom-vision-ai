from handlers.media_handler import MediaHandler
from io.handlers.typing import T, U


class FrameOutputHandler(MediaHandler):
    """
    A class that handles query outputs for a given index name.
    """

    def __init__(
        self, data_location: str
    ) -> None:
        """
        Initializes a QueryOutputHandler instance.

        Args:
            data_location (str): The location where the data is stored.
        """
        super().__init__(data_location=data_location)

    def _get_output_name(self, frame_index_name: str) -> str:
        """
        Returns the output name for a given index name.

        Args:
            frame_index_name (str): The name of the index.

        Returns:
            str: The output name.
        """
        return f"frame_index_{frame_index_name}.mp4v"

    def get_output_path(self, frame_index_name: str) -> str:
        """
        Returns the output path for a given index name.

        Args:
            frame_index_name (str): The name of the index.

        Returns:
            str: The output path.
        """
        return f"{self.data_location}/{self._get_output_name(frame_index_name)}"


    def handle_archive_by_index(self, frame_index_name: str) -> str | None:
        """
        Handles archiving of query output for a given index name.

        Args:
            frame_index_name (str): The name of the index.

        Returns:
            str | None: The output filename if successful, None otherwise.
        """
        output_filename = self._get_output_name(frame_index_name)
        return self.handle_archive(output_filename)
