import uuid
from . import file_utils

def get_uuid():
    return uuid.uuid1().hex