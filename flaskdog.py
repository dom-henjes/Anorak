import os
import sys
import random
import math
import re
import time
import numpy as np
import tensorflow as tf
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Root directory of the project
ROOT_DIR = os.path.abspath("")
sys.path.append(ROOT_DIR)

import utils
import visualize
import visualize as display_images
import model as modellib
from model import log

import skimage
import cv2
from numpy import array
from PIL import Image

# Local path to trained weights file
MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_hotdog_0030.h5")

# MS COCO Dataset
import hotdog
config = hotdog.HotdogConfig()

# Override the training configurations with a few
# changes for inferencing.
class InferenceConfig(config.__class__):
    # Run detection on one image at a time
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1

config = InferenceConfig()
config.display()

# Device to load the neural network on.
# Useful if you're training a model on the same 
# machine, in which case use CPU and leave the
# GPU for training.
DEVICE = "/cpu:0"  # /cpu:0 or /gpu:0

# Inspect the model in training or inference modes
# values: 'inference' or 'training'
# TODO: code for 'training' test mode not ready yet
TEST_MODE = "inference"

# Create model in inference mode
with tf.device(DEVICE):
    model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_PATH,
                              config=config)

model.load_weights(MODEL_PATH, by_name=True)
print("Loading weights ", MODEL_PATH)

def scale(image, max_size, method=Image.ANTIALIAS):
    """
    resize 'image' to 'max_size' keeping the aspect ratio
    and place it in center of white 'max_size' image
    """
    image.thumbnail(max_size, method)
    offset = (int((max_size[0] - image.size[0]) / 2), int((max_size[1] - image.size[1]) / 2))
    back = Image.new("RGB", max_size, "white")
    back.paste(image, offset)

    return back

def color_splash(image, mask):
    """Apply color splash effect.
    image: RGB image [height, width, 3]
    mask: instance segmentation mask [height, width, instance count]
    Returns result image.
    """
    # Make a grayscale copy of the image. The grayscale copy still
    # has 3 RGB channels, though.
    gray = skimage.color.gray2rgb(skimage.color.rgb2gray(image)) * 255
    # Copy color pixels from the original color image where mask is set
    if mask.shape[-1] > 0:
        # We're treating all instances as one, so collapse the mask into one layer
        mask = (np.sum(mask, -1, keepdims=True) >= 1)
        splash = np.where(mask, image, gray).astype(np.uint8)
    else:
        splash = gray.astype(np.uint8)
    return splash

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

@app.route('/', methods=['POST'])
@cross_origin()
def hot_or_not():
    print('Request Data:',request.data)
    image = Image.open(io.BytesIO(request.data))
    image.save(os.path.join(ROOT_DIR, "input.jpg"))
    image = Image.open(os.path.join(ROOT_DIR, "input.jpg"))
    image = scale(image, (404, 718))

    with tf.device(DEVICE):
        results = model.detect([array(image)], verbose=1)

    if (results[0]['masks'].shape[0] != 0):
        image = color_splash(array(image), results[0]['masks'])

    image = array(image)
    title = "template-hotdog.png"
    if (results[0]['masks'].shape[0] == 0):
        title = "template-not-hotdog.png"
    overlay = skimage.io.imread(title)
    alpha_s = overlay[:,:,3] / 255.0
    alpha_l = 1.0 - alpha_s
    for c in range(0,3):
        image[0:718, 0:404, c] = (alpha_s * overlay[0:718, 0:404, c]) + (alpha_l * image[0:718, 0:404, c])
    ts = time.time()
    unique_filename = str(uuid.uuid4())
    file_name = unique_filename + ".png"
    skimage.io.imsave("tmp/" + file_name, image)

    return ("http://127.0.0.1:5000/tmp/" + file_name)

@app.route('/image', methods=['POST'])
def hot_or_not_image():
    image = request.files['file']
    image.save(os.path.join(ROOT_DIR, "input.jpg"))
    image = Image.open(os.path.join(ROOT_DIR, "input.jpg"))
    image = scale(image, (404, 718))
 
    with tf.device(DEVICE):
        results = model.detect([array(image)], verbose=1)
 
    if (results[0]['masks'].shape[0] != 0):
        image = color_splash(array(image), results[0]['masks'])
 
    image = array(image)
    title = "template-hotdog.png"
    if (results[0]['masks'].shape[0] == 0):
        title = "template-not-hotdog.png"
    overlay = skimage.io.imread(title)
    alpha_s = overlay[:,:,3] / 255.0
    alpha_l = 1.0 - alpha_s
    for c in range(0,3):
        image[0:718, 0:404, c] = (alpha_s * overlay[0:718, 0:404, c]) + (alpha_l * image[0:718, 0:404, c])
    skimage.io.imsave("output.png", image)
    return send_file("output.png", mimetype='image/png')

if __name__ == '__main__':
    app.debug = False
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)