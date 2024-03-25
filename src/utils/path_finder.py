import os


def get_parent_child_path(child_dir_name):
    """Returns the path to a directory within the parent directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    return os.path.join(parent_dir, child_dir_name)
