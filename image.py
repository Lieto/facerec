'''
Created on 21.10.2015

@author: Vesa
'''
from skimage import io
from naivedlib import NaiveDlib, transformPoints, annotate

class Image:
    
    def __init__(self, cls, name, path):
        self.cls = cls
        self.name = name
        self.path = path
        self.rgb = None
    
    def getRGB(self, cache=False):
        if self.rgb is not None:
            return self.rgb
        
        else:
            try:
                rgb = io.imread(self.path)
            
            except:
                rgb = None
                
            if cache:
                self.rgb = rgb
                
            return rgb
        
    def save(self, image_format, name, path):
        # Check format is jpg
        if image_format == 'jpg':
            filename = path + name + ".jpg"
            io.imsave(filename, self.rgb)
    
    def detect_face(self):
        detector = NaiveDlib('/var/www/facerec/data/mean.csv.txt', '/var/www/facerec/data/shape_predictor_68_face_landmarks.dat')
        largestBox = detector.getLargestFaceBoundingBox(self.rgb)
        
        points = detector.align(self.rgb, largestBox)
        meanAlignPoints = transformPoints(detector.normMeanAlignPoints, largestBox, True)
        
        rectImage = annotate(self.rgb, largestBox, points = points, meanPoints = meanAlignPoints)
        
        filename = "/var/www/facerec/data/" + self.name + "_face.jpg"
        io.imsave(filename, rectImage)
    
        
    
    def __repr__(self):
        return "({}, {}".format(self.cls, self.name)
    
        
