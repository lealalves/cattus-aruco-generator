import cv2
import numpy as np

class ArucoGenerator:
    def __init__(self):
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

    def generate_single_marker(self, marker_id: int, size: int = 200, margin_size: int = 10, border_bits: int = 1) -> np.ndarray:
        marker_img = cv2.aruco.generateImageMarker(
            self.aruco_dict,
            marker_id,
            size,
            borderBits=border_bits
        )
        if margin_size > 0:
            marker_img = cv2.copyMakeBorder(
                marker_img, margin_size, margin_size, margin_size, margin_size, cv2.BORDER_CONSTANT, value=255
            )
        return marker_img
