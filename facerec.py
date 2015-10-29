import os
import requests
from flask import Flask, request, redirect, flash, url_for
from flask.helpers import send_file, send_from_directory
from image import Image
from naivedlib import NaiveDlib
from flask.templating import render_template

#DEBUG=True
#SECRET_KEY = 'development key'
#UPLOAD_FOLDER = '/var/www/facerec/data'
#UPLOAD_FOLDER = './data'

#PROCESSED_FOLDER = '/var/www/facerec/data'

#ALLOWED_EXTENSIONS = set(['jpg'])
#FACE_MEANS_FILE = 'mean.csv.txt'
#LANDMARKS_FILE = 'shape_predictor_68_face_landmarks.dat'


facerec = Flask(__name__)
#facerec.config.from_pyfile('./config.cfg', silent=True)
#Configuration

facerec.config['DEBUG'] = True
facerec.config['SECRET_KEY'] = 'development_key'
facerec.config['UPLOAD_FOLDER'] = './data'
facerec.config['PROCESSED_FOLDER'] = './data'
facerec.config['ALLOWED_EXTENSIONS'] = set(['jpg'])
facerec.config['FACE_MEANS_FILE'] = 'mean.csv.txt'
facerec.config['LANDMARKS_FILE'] = 'shape_predictor_68_face_landmarks.dat'

detector = NaiveDlib(os.path.join(facerec.config['UPLOAD_FOLDER'], facerec.config['FACE_MEANS_FILE']), 
                             os.path.join(facerec.config['UPLOAD_FOLDER'], facerec.config['LANDMARKS_FILE']), facerec)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in facerec.config['ALLOWED_EXTENSIONS']


@facerec.route('/', methods = ['GET', 'POST'])
def hello_world():
    entries = []
    
    return render_template('index.html', entries = entries)
    #return 'Hello World, Facerec application talking'

@facerec.route('/upload_from_url', methods = ['GET', 'POST'])
def upload_from_url():
    if request.method == 'POST':
        url = request.form['url']
        filename = url.split('/')[-1]
        print(url)
        image_file = requests.get(url)
        #image_file  = request.get(url)
        if image_file and allowed_file(filename):
            with open(os.path.join(facerec.config['UPLOAD_FOLDER'], filename), 'wb') as f:
                f.write(image_file.content)
                                                
            #image_file.save(os.path.join(facerec.config['UPLOAD_FOLDER'], filename))
            flash('Uploaded file')
    return '''
    <!doctype html>
    <title>Upload from url</title>
    <h1>Upload new File</h1>
    
    <form action="" method=post>
    <p><input type="text" name="url">
      <input type=submit value=Upload>
    </form>
    '''
@facerec.route('/detect_face_from_url', methods = ['GET', 'POST'])
def detect_face_from_url():
    if request.method == 'POST':
        url = request.form['url']
        filename = url.split('/')[-1]
        image_file = requests.get(url)
        
        if image_file and allowed_file(filename):
            with open(os.path.join(facerec.config['UPLOAD_FOLDER'], filename), 'wb') as f:
                f.write(image_file.content)
                
                f.close()
                
                image = Image('jpg', filename.split(".")[0], os.path.join(facerec.config['UPLOAD_FOLDER'], filename), facerec.config)
                image.getRGB(cache=True)
                
                
                largestBox = detector.getLargestFaceBoundingBox(image.rgb)
                alignedFace = detector.alignImg("homography", 256, image.rgb, largestBox, outputPrefix=image.name, outputDebug=True, expandBox=False)
            
                #image.detect_face()
        
                orig_filename = filename.split('.')[0] + "-orig" + ".jpg"
                face_imagename = filename.split('.')[0] + "-annotated" + ".jpg"
                entries = []
                entries.append(orig_filename)
                entries.append(face_imagename)
                entries.append(filename)
                return render_template('index.html', entries = entries)
                
                
                
                #image.detect_face()
        
                #face_imagename = filename.split('.')[0] + "_face" + ".jpg"
                #entries = []
                #entries.append(filename)
                #entries.append(face_imagename)
                #return render_template('index.html', entries = entries)

                        
@facerec.route('/upload', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        image_file = request.files['file']
        if image_file and allowed_file(image_file.filename):
            image_file.save(os.path.join(facerec.config['UPLOAD_FOLDER'], image_file.filename))
            flash('Uploaded file')
            
            #detect_face()

"""
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>

    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
        <input type=submit value=Upload>
    </form>
    '''
"""


@facerec.route('/get_image')
def get_image():
    image_name = request.args.get('file')
    if image_name and allowed_file(image_name):
        return send_file(os.path.join(facerec.config['UPLOAD_FOLDER'], image_name), mimetype = 'image/jpg')
    
@facerec.route('/uploads/<filename>')
def send_file(filename):
    #return send_from_directory('.', filename)
    return send_from_directory(facerec.config['UPLOAD_FOLDER'], filename)


    
@facerec.route('/detect_face_from_file', methods=['GET', 'POST'])
def detect_face_from_file():
    if request.method == 'POST':
        image_file = request.files['file']
        if image_file and allowed_file(image_file.filename):
            image_file.save(os.path.join(facerec.config['UPLOAD_FOLDER'], image_file.filename))
            image = Image('jpg', image_file.filename.split(".")[0], os.path.join(facerec.config['UPLOAD_FOLDER'], image_file.filename), facerec.config)
            image.getRGB(cache=True)
            
            largestBox = detector.getLargestFaceBoundingBox(image.rgb)
            alignedFace = detector.alignImg("homography", 256, image.rgb, largestBox, outputPrefix=image.name, outputDebug=True, expandBox=False)
            
            #image.detect_face()
        
            orig_filename = image_file.filename.split('.')[0] + "-orig" + ".jpg"
            face_imagename = image_file.filename.split('.')[0] + "-annotated" + ".jpg"
            entries = []
            entries.append(orig_filename)
            entries.append(face_imagename)
            entries.append(image_file.filename)
            return render_template('index.html', entries = entries)





if __name__ == '__main__':
    facerec.run()

        
