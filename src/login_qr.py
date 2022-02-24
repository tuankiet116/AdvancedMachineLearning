from base64 import b64decode
import os
import cv2
import tensorflow as tf
from tensorflow.keras.layers import Layer
import matplotlib.pyplot as plt
import numpy as np

threshold = 0.6

# Load class names and YOLOv3-tiny model
classes = open('qrcode.names').read().strip().split('\n')
net = cv2.dnn.readNetFromDarknet('qrcode-yolov3-tiny.cfg', 'qrcode-yolov3-tiny.weights')
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)   

def preprocess_twin(input_img, validation_img, label):
    return(preprocess(input_img), preprocess(validation_img), label)

def preprocess(frame, outs):
    frameHeight, frameWidth = frame.shape[:2]

    classIds = []
    confidences = []
    boxes = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            if confidence > threshold:
                x, y, width, height = detection[:4] * np.array(
                    [frameWidth, frameHeight, frameWidth, frameHeight])
                left = int(x - width / 2)
                top = int(y - height / 2)
                classIds.append(classId)
                confidences.append(float(confidence))
                boxes.append([left, top, int(width), int(height)])

    indices = cv2.dnn.NMSBoxes(boxes, confidences, threshold, threshold - 0.1)

    for i in indices:
        i = i
        box = boxes[i]
        left = box[0]
        top = box[1]
        width = box[2]
        height = box[3]
        cropped_image = frame[top:top + height, left:left + width]

        # Capture image QR code
        img_name = "qr_code.png"
        img = cv2.imwrite(img_name, cropped_image)
        path = "./application_data/qr_code"
        cv2.imwrite(os.path.join(path, img_name), img)

        # Draw bounding box for objects
        cv2.rectangle(frame, (left, top),
                      (left + width, top + height), (0, 0, 255))


def verify(model, detection_threshold, verification_threshold, verify_path):
    results = []
    input_img = preprocess(os.path.join(
        'application_data', 'qr_code', 'qr_code.png'))
    for image in os.listdir(verify_path):
        print(image)
        validation_img = preprocess(os.path.join(verify_path, image))
        # Dự đoán
        result = model.predict(
            list(np.expand_dims([input_img, validation_img], axis=1)))
        results.append(result)

    # Ngưỡng nhận diện: Chỉ số dự đoán lớn hơn ngưỡng dự đoán
    detection = np.sum(np.array(results) > detection_threshold)
    # Ngưỡng Verified: Tỷ lệ dự đoán ảnh đúng(positive)  / Tổng số lượng ảnh của người nhận diện (positive)
    verification = detection / \
        len(os.listdir(os.path.join('application_data', 'verification_images')))
    verified = verification > verification_threshold

    return results, verified


def login_check(image):
    input_path = os.path.join(
        'application_data', 'qr_code', 'qr_code.png')

    header, encoded = image.split(",", 1)
    with open(input_path, "wb") as f:
        f.write(b64decode(encoded))

    try:
        try:
            
            if(verified == True):
                return "Successfully Logged in!"
            else:
                return "Login Fail"
        except Exception as e:
            print(e.__cause__)
            return "Data does not exist!"
    except Exception as e:
        print(e.__cause__)
        return "Image not clear! Please try again!"
