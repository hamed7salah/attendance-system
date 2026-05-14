"""Computer Vision pipeline package"""

from .detector import FaceDetector
from .recognizer import FaceRecognizer
from .tracker import FaceTracker

__all__ = ['FaceDetector', 'FaceRecognizer', 'FaceTracker']
