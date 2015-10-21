'''
Created on 21.10.2015

@author: Vesa
'''
import dlib
import numpy as np
import cv2

class NaiveDlib:
    
    def __init__(self, faceMean, facePredictor):
        
        self.detector = dlib.get_frontal_face_detector()
        self.normMeanAlignPoints = loadMeanPoints(faceMean)
        self.predictor = dlib.shape_predictor(facePredictor)
        
    def getAllFaceBoundingBoxes(self, img):
        return self.detector(img, 1)
    
    def getLargestFaceBoundingBox(self, img):
        faces = self.detector(img, 1)
        if len(faces) > 0:
            return max(faces, key = lambda rect: rect.width() * rect.height())
        
    def align(self, img, bb):
        points = self.predictor(img, bb)
        return list(map(lambda p: (p.x, p.y), points.parts()))
    

def loadMeanPoints(modelFname):
    def parse(line):
        (x, y) = line.strip().split(",")
        return (float(x), float(y))
    
    with open(modelFname, 'r') as f:
        return [parse(line) for line in f]

def transformPoints(points, bb, toImgCoords):
    if toImgCoords:
        def scale(p):
            (x, y) = p
            return (int((x * bb.width()) + bb.left()),
                    int((y * bb.height()) + bb.top()))
            
    else:
        def scale(p):
            (x, y) = p
            return (float(x - bb.left()) / bb.width(),
                    float(y - bb.top()) / bb.height())
    
    return list(map(scale, points))

def annotate(img, box, points=None, meanPoints=None):
    a = np.copy(img)
    bl = (box.left(), box.bottom())
    tr = (box.right(), box.top())
    cv2.rectangle(a, bl, tr, color = (153, 255, 204), thickness= 3)
    
    for p in points:
        cv2.circle(a, center = p, radius = 3, color=(102, 204, 255), thickness = -1)
    
    for p in meanPoints:
        cv2.circle(a, center=p, radius=3, color=(0, 0, 0), thickness=-1)
        
    return a


    
    
