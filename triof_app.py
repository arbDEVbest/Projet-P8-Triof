from distutils.command.upload import upload
from importlib.resources import path
import pathlib
from flask import Flask, render_template, request
from itsdangerous import base64_decode, base64_encode
from werkzeug.utils import secure_filename
from src.prediction_cloud_premise import response_prediction, on_premise_class_predict
from src.utils import *
from keras.models import load_model
import tensorflow as tf
import numpy as np
import base64
from pathlib import Path

uploadImage = Path.cwd()/"camera"/"uploadImage"
model = load_model('vgg_16_-saved-model-52-acc-0.85.hdf5')
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/start')
def insert():
    open_waste_slot()
    return render_template('insert.html')

@app.route('/waste/pick-type',methods = ['GET', 'POST'])
def pick_type():
    if request.method == 'POST':
        f = request.files.get("image")
        #decoded = base64.b64decode(f.getvalue())
        selectedValue = request.form['option']
        if selectedValue == "cloud":
            probability, tagName = response_prediction(f.getvalue())
            option=True
        else:
            probability,tagName = on_premise_class_predict(f.read(),model,(250,250,3))
            option=False
        close_waste_slot()
        return render_template('type.html', type=tagName, proba=round(float(probability)*100,2), option=option)


@app.route('/confirmation', methods=['POST'])
def confirmation():
    waste_type = request.form['type']

    process_waste(waste_type)
    return render_template('confirmation.html')


if __name__ == "__main__":
    app.run(debug=True)
