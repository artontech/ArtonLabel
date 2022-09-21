''' pic '''
import cv2
import numpy as np


def bytes2cv(data: bytes) -> np.ndarray:
    ''' bytes to opencv '''
    return cv2.imdecode(np.array(bytearray(data), dtype="uint8"), cv2.IMREAD_UNCHANGED)


def cv2bytes(img: np.ndarray, format: str = ".png") -> bytes:
    ''' opencv to bytes '''
    return np.array(cv2.imencode(format, img)[1]).tobytes()

def cv2transparent(img: np.ndarray, color: int):
    ''' set transparent color TODO: support custom color '''
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
    else:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    b=np.ones((img.shape[0],img.shape[1],3),dtype=np.uint8)*color
    c=np.array(np.sum(img[:,:,:3]==b,axis=-1)/3,dtype=np.uint8)
    img[:,:,-1][c==1]=0
    return img
