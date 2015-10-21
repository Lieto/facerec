import os
import requests
from flask import Flask, request, redirect, flash, url_for
from flask.helpers import send_file, send_from_directory
from image import Image
from flask.templating import render_template

DEBUG=True
SECRET_KEY = 'development key'
#UPLOAD_FOLDER = '/var/www/facerec/data'
UPLOAD_FOLDER = './data/'
PROCESSED_FOLDER = '/var/www/facerec/data'

ALLOWED_EXTENSIONS = set(['jpg'])

facerec = Flask(__name__)
facerec.config.from_object(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@facerec.route('/')
def hello_world():
    return 'Hello World, Facerec application talking'

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
        
@facerec.route('/upload', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        image_file = request.files['file']
        if image_file and allowed_file(image_file.filename):
            image_file.save(os.path.join(facerec.config['UPLOAD_FOLDER'], image_file.filename))
            flash('Uploaded file')
            
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>

    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
        <input type=submit value=Upload>
    </form>
    '''

@facerec.route('/get_image')
def get_image():
    image_name = request.args.get('file')
    if image_name and allowed_file(image_name):
        return send_file(os.path.join(facerec.config['UPLOAD_FOLDER'], image_name), mimetype = 'image/jpg')
    
@facerec.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(facerec.config['UPLOAD_FOLDER'], filename)

    
@facerec.route('/detect_face', methods=['GET', 'POST'])
def detect_face():
    if request.method == 'POST':
        image_file = request.files['file']
        if image_file and allowed_file(image_file.filename):
            image_file.save(os.path.join(facerec.config['UPLOAD_FOLDER'], image_file.filename))
            image = Image('jpg', image_file.filename.split(".")[0], os.path.join(facerec.config['UPLOAD_FOLDER'], image_file.filename))
            image.getRGB(cache=True)
            image.detect_face()
        
            face_imagename = image_file.filename.split('.')[0] + "_face" + ".jpg"
            entries = []
            entries.append(image_file.filename)
            entries.append(face_imagename)
            return render_template('show_images.html', entries = entries)
            #return redirect(url_for('show_images'))
            #return send_file(os.path.join(facerec.config['UPLOAD_FOLDER'], face_imagename), mimetype = 'image/jpg')
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
        <p><input type=file name=file>
        <input type=submit value=Upload>
    </form>
    '''




if __name__ == '__main__':
    facerec.run()

        
