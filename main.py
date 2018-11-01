"""Emotion Detetion Module.

This module detects the emotion of visitors.

"""
from __future__ import absolute_import
import cv2
from keras.models import load_model
import collections
import numpy as np
from datetime import timedelta
from datetime import datetime as dt
from aceva.utils.inference import apply_offsets
import aceva.utils.Face as Face
from aceva.utils.helper import post
from aceva.utils.datasets import get_labels
from aceva.utils.inference import detect_faces, draw_text, draw_bounding_box
from aceva.utils.inference import load_detection_model
from aceva.utils.preprocessor import preprocess_input
from statistics import mode


def emotionVideo(mac, url, emoprod_post, cam_data):
    """Detect emotion in given video URL."""
    detection_model_path = './aceva/emotion/trained_models/detection_models/haarcascade_frontalface_default.xml'
    emotion_model_path = './aceva/emotion/trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5'
    gender_model_path = './aceva/emotion/trained_models/gender_models/simple_CNN.81-0.96.hdf5'

    emotion_labels = get_labels('fer2013')
    gender_labels = get_labels('imdb')

    # hyper-parameters for bounding boxes shape
    gender_offsets = (30, 60)
    emotion_offsets = (20, 40)

    # loading models
    face_detection = load_detection_model(detection_model_path)
    emotion_classifier = load_model(emotion_model_path, compile=False)
    gender_classifier = load_model(gender_model_path, compile=False)

    # getting input model shapes for inference
    emotion_target_size = emotion_classifier.input_shape[1:3]
    gender_target_size = gender_classifier.input_shape[1:3]

    # starting lists for calculating modes
    gender_window = []
    emotion_window = []
    fid = 1
    max_age = 100
    target_distance = 50
    # starting video streaming
    cv2.namedWindow(cam_data['adv_title'])
    pre_time = dt.now()
    video_capture = cv2.VideoCapture(cam_data['cam_url'])
    faces = []
    while True:
        bgr_image = video_capture.read()[1]
        try:
            gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
            rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
        except Exception as e:
            print(e, 'Reopening the camera...')
            video_capture = cv2.VideoCapture(cam_data['cam_url'])

        try:        
            detectFaces = detect_faces(face_detection, gray_image)
        except Exception as e:
            print(e, 'Reopening the camera...')
            video_capture = cv2.VideoCapture(cam_data['cam_url'])
            continue
    
        new = True

        for i in faces:
            i.age_one()

        for face_coordinates in detectFaces:
            for i in faces:

                if abs(face_coordinates[0]-i.getX()) <= target_distance\
                        and abs(face_coordinates[1]-i.getY())\
                        <= target_distance:
                    new = False
                    i.updateCoords(face_coordinates[0], face_coordinates[1])
                    cur_id = i.getId()
                    print(cam_data['adv_title'], " Repeated FaceID:",
                          cur_id, "Detected")

            if new:
                f = Face.MyFace(fid, face_coordinates[0],
                                face_coordinates[1], max_age)
                faces.append(f)
                cur_id = f.getId()
                print(cam_data['adv_title'], " New FaceID:",
                      cur_id, "Detected")
                fid += 1

            x1, x2, y1, y2 = apply_offsets(face_coordinates, gender_offsets)

            rgb_face = rgb_image[y1:y2, x1:x2]

            x1, x2, y1, y2 = apply_offsets(face_coordinates, emotion_offsets)
            gray_face = gray_image[y1:y2, x1:x2]

            try:
                rgb_face = cv2.resize(rgb_face, (gender_target_size))
            except Exception as e:
                print(e, 'Reopening the camera')
                video_capture = cv2.VideoCapture(cam_data['cam_url'])
                continue

            try:
                gray_face = cv2.resize(gray_face, (emotion_target_size))
            except Exception as e:
                print(e, 'Reopening the camera')
                video_capture = cv2.VideoCapture(cam_data['cam_url'])
                continue

            gray_face = preprocess_input(gray_face, False)
            gray_face = np.expand_dims(gray_face, 0)
            gray_face = np.expand_dims(gray_face, -1)
            emotion_label_arg = np.argmax(
                emotion_classifier.predict(gray_face))
            emotion_text = emotion_labels[emotion_label_arg]

            rgb_face = np.expand_dims(rgb_face, 0)
            rgb_face = preprocess_input(rgb_face, False)
            gender_prediction = gender_classifier.predict(rgb_face)
            gender_label_arg = np.argmax(gender_prediction)
            gender_text = gender_labels[gender_label_arg]

            for i in faces:
                if i.getId() == cur_id:
                    i.updateEmotion(emotion_text)
                    i.updateGender(gender_text)

            if emotion_text == 'neutral':
                emotion_mode = emotion_text
            elif emotion_text in ['happy', 'surprise']:
                emotion_mode = 'interested'
            else:
                emotion_mode = 'not interested'

            if gender_text == gender_labels[0]:
                color = (0, 0, 255)
            else:
                color = (255, 0, 0)

            draw_bounding_box(face_coordinates, rgb_image, color)
            draw_text(face_coordinates, rgb_image, gender_text, color,
                      0, -20, 1, 2)
            draw_text(face_coordinates, rgb_image, emotion_mode, color,
                      0, -45, 1, 2)

        next_sent = pre_time + timedelta(minutes=5)
        now = dt.now()
        next_str = next_sent.strftime('%M')
        now_str = now.strftime('%M')

        if now_str == next_str:
            pre_time = now
            date = dt.now().strftime("%Y%m%d")
            time_stamp = dt.now().strftime("%Y/%m/%d %H:%M")
            for i in faces:
                try:
                    gender_window.append(mode(i.getGender()))
                except Exception as e:
                    print(e, 'Taking the default man')
                    gender_window.append('man')
                try:
                    emotion_window.append(mode(i.getEmotion()))
                except Exception as e:
                    print(e, 'Taking the default neutral')
                    emotion_window.append('neutral')
            print(cam_data['adv_title'])
            print(gender_window)
            print(emotion_window)
            gender = dict(collections.Counter(gender_window))
            emo = dict(collections.Counter(emotion_window))
            neutral = 0
            interested = 0
            notinterested = 0
            for key, value in emo.items():
                if key == 'neutral':
                    neutral += value
                elif key in ['happy', 'surprise']:
                    interested += value
                else:
                    notinterested += value

            if 'man' not in gender.keys():
                gender['man'] = 0
            if 'woman' not in gender.keys():
                gender['woman'] = 0
            if 'adv_title' is not cam_data.keys():
                cam_data['adv_title'] = cam_data['adv_title']
            data = {
                "date": date,
                "time_stamp": time_stamp,
                "male": gender['man'],
                "female": gender['woman'],
                "advert_title": cam_data['adv_title'],
                "neutral": neutral,
                "interested": interested,
                "notinterested": notinterested
            }

            auth = 'key='+mac+' emo'
            status, code = post(url, emoprod_post, auth, data)
            print(data)

            if code == 200:
                gender_window = []
                emotion_window = []
                faces = []
        try:
            bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
            cv2.imshow(cam_data['adv_title'], bgr_image)
        except Exception as e:
            print(e, 'Reopening the camera...')
            video_capture = cv2.VideoCapture(cam_data['cam_url'])

        if cv2.waitKey(1) & 0xFF == 27:  # ESC key
            break
