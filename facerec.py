import os
from flask import Flask, request, flash
from flask.helpers import send_file

DEBUG=True
UPLOAD_FOLDER = '/var/www/facerec/data'
PROCESSED_FOLDER = '/var/www/facerec/data'

ALLOWED_EXTENSIONS = set(['jpg'])

facerec = Flask(__name__)
facerec.config.from_object(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@facerec.route('/')
def hello_world():
    return 'Hello World, Facerec application talking'
    
@facerec.route('/upload', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        image_file = request.files['file']
        if image_file and allowed_file(image_file.filename):
            file.save(os.path.join(facerec.config['UPLOAD_FOLDER'], image_file.filename))
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

if __name__ == '__main__':
    facerec.run()

        
