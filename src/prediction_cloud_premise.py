import json
import requests
import os 
import io
import numpy as np
from pathlib import Path
from keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image

# Add your Face subscription key and endpoint to your environment variables.
subscription_key = os.getenv("PREDICTION_KEY", "5977f17374e249d6882db717a188c80b")
endpoint = os.getenv("CUSTOM_VISION_ENDPOINT","https://fetcostumvision-prediction.cognitiveservices.azure.com/customvision/v3.0/Prediction/ab3c146b-7abc-431d-a00a-3ee91cb39264/classify/iterations/Iteration1/image")

# Request headers.
headers = {
    'Content-Type': 'application/octet-stream',
    'Prediction-Key': subscription_key,
}

def response_prediction(image, endpoint=endpoint, headers=headers):
    """
    returns the prediction of azure's computer vision returns the probability and class of the image
    param image : image to predict
    param endpoint : Simply put, an API endpoint is the entry point into a communication channel to azure cloud(computer vision)
    param headers : are HTTP the code that transfers data between a Web server and a client
    """
    
    response = requests.post(url=endpoint,headers=headers,data=image)
    prediction =  response.json()
    probability = prediction["predictions"][0]["probability"]
    tagName = prediction["predictions"][0]["tagName"]
    return f'{probability:.04f}', tagName

def on_premise_class_predict(decoded_img,model_cnn, image_shape):
    """
    returns the probability of the on-premise model and its class
    param path_image : path of image to predict
    param path_model_cnn : path of on-premise model
    param image_shape: size of array image 
    """
    
    my_img = Image.open(io.BytesIO(decoded_img)).resize(image_shape[:-1],Image.LANCZOS).convert("RGB") #load image predict and resize it
    img = np.asarray(my_img)/255
    print("Ici image taille: ",img.shape)
    img_array = np.expand_dims(img,axis=0) # reshape image array and adding one dimension (1,width,heigth,canal_size)
    print("Ici image reshape: ",img_array.shape)
    max_acc = model_cnn.predict(img_array).max()#max probability
    rest = np.argmax((model_cnn.predict(img_array) > 0.5).astype('int32'))# get the index of max probability
    switch={
        0:"bouteille-propre",
        1:"bouteille-sale",
        2:"couvert-propre",
        3:"couvert-sale",
        4:"goblet-propre",
        5:"goblet-sale"
    }
    return f'{max_acc:.04f}',switch.get(rest)
