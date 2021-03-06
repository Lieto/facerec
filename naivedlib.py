'''
Created on 21.10.2015

@author: Vesa
'''
import sys, os, errno
import dlib
import numpy as np
import cv2

from skimage import io

def mkdirP(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class NaiveDlib:
    
    def __init__(self, faceMean, facePredictor, facerec):
        
        self.facerec = facerec
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
    
    def alignImg(self, method, size, img, bb=None,
                 outputPrefix=None, outputDebug=False,
                 expandBox=False):
        
        if outputPrefix:
            #mkdirP(os.path.dirname(outputPrefix))
            
            def getName(tag=None):
                if tag is None:
                    return "{}.jpg".format(outputPrefix)
                else:
                    return "{}-{}.jpg".format(outputPrefix, tag)
                
        if bb is None:
            try:
                bb = self.getLargestFaceBoundingBox(img)
            except Exception as e:
                print("Warning: {}".format(e))
                # IN rare cases, exceptions are thrown.
                return
                
            if bb is None:
                # Most failed detection attempts return here
                return
        
        alignPoints = self.align(img, bb)
        meanAlignPoints = transformPoints(self.normMeanAlignPoints, bb, True)
        
        (xs, ys) = zip(*meanAlignPoints)
        tightBb = dlib.rectangle(left=min(xs), right=max(xs),
                                 top=min(ys), bottom=max(ys))
        
        if method != 'tightcrop':
            npAlignPoints = np.float32(alignPoints)
            npMeanAlignPoints = np.float32(meanAlignPoints)
        if method == 'tightcrop':
            warpedImg = img
        elif method == 'affine':
            ss = np.array([39, 42, 57]) #Eyes and tip of nose
            npAlignPointsSS = npAlignPoints[ss]
            npMeanAlignPointsSS = npMeanAlignPoints[ss]
            H = cv2.getAffineTransform(npAlignPointsSS, npMeanAlignPointsSS)
            warpedImg = cv2.warpAffine(img, H, np.shape(img)[0:2])
        elif method == 'perspective':
            ss = np.array([39, 42, 48, 54]) # Eyes and corners of mouth
            npAlignPointSS = npAlignPoints[ss]
            npMeanAlignPointsSS = npMeanAlignPoints[ss]
            H = cv2.getPerspectiveTransform(npAlignPointSS, npMeanAlignPointsSS)
            warpedImg = cv2.warpPerspective(img, H, np.shape(img)[0:2])
        elif method == 'homography':
            (H, mask) = cv2.findHomography(npAlignPoints, npMeanAlignPoints,
                                           method = cv2.LMEDS)
            warpedImg = cv2.warpPerspective(img, H, np.shape(img)[0:2])
        else:
            print("Error: method '{}' is unimplemented.".format(method))
            sys.exit(-1)
            
        if method == 'tightcrop':
            wAlignPoints = alignPoints
        else:
            wBb = self.getLargestFaceBoundingBox(warpedImg)
            if wBb is None:
                return
            wAlignPoints = self.align(warpedImg, wBb)
            wMeanAlignPoints = transformPoints(self.normMeanAlignPoints, wBb, True)
            
        if outputDebug:
            annotatedImg = annotate(img, bb, alignPoints, meanAlignPoints)
            image_name = os.path.join(self.facerec.config['UPLOAD_FOLDER'], getName("orig"))
            annotated_image_name = os.path.join(self.facerec.config['UPLOAD_FOLDER'], getName("annotated"))
            io.imsave(image_name, img)
            io.imsave(annotated_image_name, annotatedImg)
            
            if method != 'tightcrop':
                wAnnotatedImg = annotate(warpedImg, wBb,
                                         wAlignPoints, wMeanAlignPoints)
                
                warped_image_name = os.path.join(self.facerec.config['UPLOAD_FOLDER'], getName("warped"))
                annotated_image_name = os.path.join(self.facerec.config['UPLOAD_FOLDER'], getName("warped-annotated"))
                
                io.imsave(warped_image_name, warpedImg)
                #io.imsave(getName("warped"), warpedImg)
                io.imsave(annotated_image_name, wAnnotatedImg)
                
        if len(warpedImg.shape) != 3:
            print(" + Warning: result does not have 3 dimensions.")
            return None
        
        (xs, ys) = zip(*wAlignPoints)
        xRange = max(xs) - min(xs)
        yRange = max(ys) - min(ys)
        
        if expandBox:
            (l, r, t, b) = (min(xs) - 0.20 * xRange, max(xs) + 0.20 * xRange,
                            min(ys)- 0.65 * yRange, max(ys) + 0.20 * yRange)
        else:
            (l, r, t, b) = (min(xs), max(xs), min(ys), max(ys))
        
        (w, h, _) = warpedImg.shape
        
        if 0 <= l <= w and 0 <= r <= w and 0 <= b <= h and 0 <= t <= h:
            cwImg = cv2.resize(warpedImg[t : b, l : r], (size, size))
            h, edges = np.histogram(cwImg.ravel(), 16, [0, 256])
            s = sum(h)
            if any(h > 0.65 * s):
                print("Warning: Image is likely a single color.")
                return
        else:
            print("Warning: Unable to align and crop to the face's bounding box.")
            return
            
        if outputPrefix:
            cropped_image_name  =  os.path.join(self.facerec.config['UPLOAD_FOLDER'], getName("cropped"))
            io.imsave(cropped_image_name, cwImg)
        return cwImg

    

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


    
    
