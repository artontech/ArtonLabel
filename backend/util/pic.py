''' pic '''
import cv2
import numpy as np


def bytes2cv(data: bytes) -> np.ndarray:
    ''' bytes to opencv '''
    return cv2.imdecode(np.array(bytearray(data), dtype="uint8"), cv2.IMREAD_UNCHANGED)


def cv2bytes(img: np.ndarray, format: str = ".png") -> bytes:
    ''' opencv to bytes '''
    return np.array(cv2.imencode(format, img)[1]).tobytes()
