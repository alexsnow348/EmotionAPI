from __future__ import absolute_import

from flask import Flask, request, Response, render_template, jsonify
import jsonpickle
import numpy as np
import cv2
import simplejson
import json
import cv2
from keras.models import load_model
import collections
from datetime import timedelta
from datetime import datetime as dt
from utils.inference import apply_offsets
import utils.Face as Face
from utils.datasets import get_labels
from utils.inference import detect_faces, draw_text, draw_bounding_box
from utils.inference import load_detection_model
from utils.preprocessor import preprocess_input
# Initialize the Flask application
app = Flask(__name__)

detection_model_path = './trained_models/detection_models/haarcascade_frontalface_default.xml'
emotion_model_path = './trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5'
gender_model_path = './trained_models/gender_models/simple_CNN.81-0.96.hdf5'
emotion_labels = get_labels('fer2013')
gender_labels = get_labels('imdb')
gender_offsets = (30, 60)
emotion_offsets = (20, 40)


@app.route('/api/test', methods=['POST'])
def test():
    if request.method == 'POST':
        # convert string of image data to uint8
        nparr = np.fromstring(request.data, np.uint8)
        # decode image
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        # write the image in the folder
        # cv2.imwrite('image.jpeg', img)

        face_detection = load_detection_model(detection_model_path)
        emotion_classifier = load_model(emotion_model_path, compile=False)
        gender_classifier = load_model(gender_model_path, compile=False)

        emotion_target_size = emotion_classifier.input_shape[1:3]
        gender_target_size = gender_classifier.input_shape[1:3]

        gender_window = []
        emotion_window = []
        faces = []
        # bgr_image = cv2.imread('image.jpeg')
        bgr_image = img
        gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
        rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)

        detectFaces = detect_faces(face_detection, gray_image)

        # print('Total Face:', len(detectFaces))#comment it out
        for face_coordinates in detectFaces:
            x1, x2, y1, y2 = apply_offsets(face_coordinates, gender_offsets)
            # print(face_coordinates)
            rgb_face = rgb_image[y1:y2, x1:x2]
            x1, x2, y1, y2 = apply_offsets(face_coordinates, emotion_offsets)
            gray_face = gray_image[y1:y2, x1:x2]
            rgb_face = cv2.resize(rgb_face, (gender_target_size))
            gray_face = cv2.resize(gray_face, (emotion_target_size))

            gray_face = preprocess_input(gray_face, False)
            gray_face = np.expand_dims(gray_face, 0)
            gray_face = np.expand_dims(gray_face, -1)
            try:
                emotion_label_arg = np.argmax(
                    emotion_classifier.predict(gray_face))
                emotion_text = emotion_labels[emotion_label_arg]
            except ValueError:
                emotion_text = "undefined"

            rgb_face = np.expand_dims(rgb_face, 0)
            rgb_face = preprocess_input(rgb_face, False)
            try:
                gender_prediction = gender_classifier.predict(rgb_face)
                gender_label_arg = np.argmax(gender_prediction)
                gender_text = gender_labels[gender_label_arg]
            except ValueError:
                gender_text = "undefined"

            face = dict()
            face['faceRectangle'] = {
                "top": str(face_coordinates[0]),
                "left": str(face_coordinates[1]),
                "width": str(face_coordinates[2]),
                "height": str(face_coordinates[3])
            }
            face['emotion'] = emotion_text
            face['gender'] = gender_text
            faces.append(face)

            faces_pickled = json.dumps(faces)
            coordinates = json.dumps(face['faceRectangle'])

        # encode response using jsonpickle
        if len(faces) > 0:
            response_pickled = jsonpickle.encode(faces)
            # return faces
            return Response(response=faces_pickled, status=200, mimetype="application/json")
        else:
            message = {'message': 'Please use another image'}
            message_pickled = jsonpickle.encode(message)
            return Response(response=message_pickled, status=200, mimetype="application/json")


# start flask app

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
