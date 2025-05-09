# utils/file_utils.py

import os

def traversal_files(base):
    """
    Traverse all files in the base directory.
    """
    for root, ds, fs in os.walk(base):
        for f in fs:
            fullname = os.path.join(root, f)
            yield fullname

def get_project_base_directory():
    """
    Get the project base directory.
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))