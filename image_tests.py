'''
Created on 21.10.2015

@author: Vesa
'''
import unittest
import os.path

from image import Image

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_save_jpg(self):
        #Read jpg file to image
        orig_image = Image("jpg", "1", "./data/1.jpg")
        orig_image.getRGB(cache=True)
        
        # Save it to name + test - jpg image
        filename = orig_image.name + "_test"
        orig_image.save('jpg', filename, "./data/")
        #Check there is file called name + test image in directory
        self.assertTrue(os.path.exists("./data/1_test.jpg"))
        
        os.remove('./data/1_test.jpg')
        
        #Check the size of image is the same as original
        #self.assertEqual(os.stat("./1.jpg").st_size, os.stat("./1_test.jpg").st_size)
        
    def test_detect_face(self):
        orig_image = Image("jpg", "1", "./data/1.jpg")
        orig_image.getRGB(cache=True)
        
        orig_image.detect_face()
        
        self.assertTrue(os.path.exists("./data/1_face.jpg"))
        
        #os.remove('./data/1_face.jpg')

        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_save_jpg']
    unittest.main()
