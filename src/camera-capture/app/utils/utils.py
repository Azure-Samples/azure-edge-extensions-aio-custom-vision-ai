def get_frame_file_name(prefix: str, dev_node_name: str, index: int) -> str:
    return f"{prefix}-{dev_node_name.lower()}-{index}"
