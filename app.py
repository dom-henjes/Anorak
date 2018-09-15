import keras
from keras.models import load_model
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras import optimizers
from keras.layers import *
from PIL import Image
# import skimage
import os, os.path
import matplotlib.pyplot as plt
import numpy as np
from keras.callbacks import EarlyStopping
import time

from flask import Flask
from flask_cors import CORS, cross_origin
from flask import request
from flask import send_file
import io
import time
import uuid

app = Flask(__name__, static_url_path = "/tmp", static_folder = "tmp")
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Local path to trained weights file
MODEL_PATH = "coeus_weights.h5"
DATA_PATH = '../../data/extracted_images'

earlystop = EarlyStopping(monitor='val_acc', mode='auto')
callbacks_list = [earlystop]

def train_model():
    global DATA_PATH, callbacks_list

    train_datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)
    train_generator = train_datagen.flow_from_directory(
            DATA_PATH,
            target_size=(45, 45),
            batch_size=64,
            color_mode='grayscale',
            class_mode='categorical',
            subset='training')

    val_generator = train_datagen.flow_from_directory(
            DATA_PATH,
            target_size=(45, 45),
            batch_size=64,
            color_mode='grayscale',
            class_mode='categorical',
            subset='validation')

    model_1 = fetch_model()
    model_1.fit_generator(
        train_generator,
        epochs=20,
        validation_data = val_generator,
        callbacks=callbacks_list)

    model_1.save('new_weights.h5')
    print('New weights saved')

    return model_1

def load_model():
    global MODEL_PATH
    model_1 = fetch_model()
    model_1.load_weights(MODEL_PATH)

def fetch_model():
    # CNN using Keras' Sequential
    model_1 = Sequential()

    ## 5x5 convolution with 2x2 stride and 32 filters
    model_1.add(Conv2D(64, (5, 5), strides = (2,2), input_shape=(45, 45, 1)))
    model_1.add(Activation('relu'))

    ## 2x2 max pooling reduces to 3 x 3 x 32
    model_1.add(MaxPooling2D(pool_size=(2, 2)))
    model_1.add(Dropout(0.25))

    ## Another 5x5 convolution with 2x2 stride and 32 filters
    model_1.add(Conv2D(64, (5, 5), strides = (1,1)))
    model_1.add(Activation('relu'))

    ## 2x2 max pooling reduces to 3 x 3 x 32
    model_1.add(MaxPooling2D(pool_size=(2, 2)))
    model_1.add(Dropout(0.25))

    ## Flatten turns 3x3x32 into 288x1
    model_1.add(Flatten())
    model_1.add(Dense(512))
    model_1.add(Activation('relu'))
    model_1.add(Dropout(0.5))
    model_1.add(Dense(84))
    model_1.add(Activation('softmax'))

    model_1.compile(loss='categorical_crossentropy',
                    optimizer=optimizers.RMSprop(lr=0.0005, decay=1e-6),
                    metrics=['accuracy'])
    return model_1


import os, requests
 
def formula_as_file( formula, file, negate=False ):
    tfile = file
    if negate:
        tfile = 'tmp.png'
    r = requests.get( 'http://latex.codecogs.com/png.latex?\dpi{300} \huge %s' % formula )
    f = open( tfile, 'wb' )
    f.write( r.content )
    f.close()
    if negate:
        os.system( 'convert tmp.png -channel RGB -colorspace rgb %s' %file )

def load_binary(file):
    with open(file, 'rb') as file:
        return file.read()

@app.route('/', methods=['POST'])
@cross_origin()
def fetch_latex():
    FILE_NAME = 'formula.png';

    equation_doodle = request.data;
    image = Image.open(io.BytesIO(equation_doodle))
   
    ## Process image and get a LateX syntax placed into a string
    ## Generate the LateX image and send it back with the LateX syntax (put a separator in between)
    latex_syntax = r'\Gamma_{Levin}(x) = \| \nabla p(x) \|_2^{0.8} + \sum_i |\frac{\partial^2 p(x)}{\partial x_i^2}|^{0.8}';
    formula_as_file( r'\Gamma_{Levin}(x) = \| \nabla p(x) \|_2^{0.8} + \sum_i |\frac{\partial^2 p(x)}{\partial x_i^2}|^{0.8}', FILE_NAME, True)

    ## Send the image back to the chatbot

    import base64
    with open(FILE_NAME, "rb") as imageFile:
      str = base64.b64encode(imageFile.read())
      print(str);

    formula_image = str;

    
    return formula_image, latex_syntax;

    model = load_model()
    estimate = model.predict(request.data) # or should this take 'image' instead?


