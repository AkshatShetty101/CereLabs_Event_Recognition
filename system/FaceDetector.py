# FaceDetector.

import cv2
import numpy as np
import os
import glob
import dlib
import sys
import argparse
from PIL import Image
import math
import datetime
import threading
import logging
import ImageUtils

class FaceDetector(object):
    """This class implements Dlib's HOG based face detector"""

    def __init__(self):
        self.facecascade = cv2.CascadeClassifier("cascades/haarcascade_frontalface_alt2.xml")
        self.facecascade2 = cv2.CascadeClassifier("cascades/haarcascade_frontalface_alt2.xml")
        self.detector = dlib.get_frontal_face_detector()
        self.cascade_lock = threading.Lock()
        self.accurate_cascade_lock = threading.Lock()


    def detect_faces(self,image,dlibDetector):
         if dlibDetector:
            return self.detect_dlib_face(image)
         else:
            return self.detect_cascade_face(image)

    def pre_processing(self,image):
         """Performs CLAHE on a greyscale image"""
         grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
         clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
         cl1 = clahe.apply(grey)
         #cl1 = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
         return cl1


    def rgb_pre_processing(self,image):
        """Performs CLAHE on each RGB components and rebuilds final
        normalised RGB image - side note: improved face detection not recognition"""
        (h, w) = image.shape[:2]    
        zeros = np.zeros((h, w), dtype="uint8")
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(10,10))
        (B, G, R) = cv2.split(image)
        R = clahe.apply(R)
        G = clahe.apply(G)
        B = clahe.apply(B)
        filtered = cv2.merge([B, G, R])
        cv2.imwrite('notfilteredRGB.jpg',image)
        cv2.imwrite('filteredRGB.jpg',filtered)
        return filtered


    def detect_dlib_face(self,image):
        image = self.pre_processing(image)
        bbs = self.detector(image, 1)
        return bbs  

    def detect_cascade_face(self,image):
        with self.cascade_lock:  # Used to block simultaneous access to resource, stops segmentation fault when using more than one camera
            image = self.pre_processing(image)
            rects = self.facecascade.detectMultiScale(image, scaleFactor=1.25, minNeighbors=3, minSize=(20, 20), flags = cv2.CASCADE_SCALE_IMAGE)
        return rects

    def detect_cascadeface_accurate(self,img):
        """Used to help mitigate false positive detections"""
        with self.accurate_cascade_lock:
            rects = self.facecascade2.detectMultiScale(img, scaleFactor=1.02, minNeighbors=12, minSize=(20, 20), flags = cv2.CASCADE_SCALE_IMAGE)
        return rects