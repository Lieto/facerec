import os
from flask import Flask, request, flash
from flask.helpers import send_file

#DEBUG=True
#UPLOAD_FOLDER = '/var/www/facerec/data'
#PROCESSED_FOLDER = '/var/www/facerec/data'

ALLOWED_EXTENSIONS = set(['jpg'])

facerec = Flask(__name__)
facerec.config.from_object(__name__)

@facerec.route('/')
def hello_world():
    return 'Hello World, Facerec application talking'

if __name__ == '__main__':
    facerec.run()

        
