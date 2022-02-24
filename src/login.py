from base64 import b64decode
import os
import cv2
import tensorflow as tf
from tensorflow.keras.layers import Layer
import matplotlib.pyplot as plt
import numpy as np


class L1Dist(Layer):
    def __init__(self, **kwargs):
        super().__init__()
       
    # Tính toán khoảng cách
    def call(self, input_embedding, validation_embedding):
        print(tf.math.abs(input_embedding - validation_embedding))
        return tf.math.abs(input_embedding - validation_embedding)
    
def preprocess_twin(input_img, validation_img, label):
    return(preprocess(input_img), preprocess(validation_img), label)

def preprocess(file_path):
    # Đọc ảnh 
    byte_img = tf.io.read_file(file_path)
    # Load ảnh 
    img = tf.io.decode_jpeg(byte_img)
    
    # Tiền xử lý chuyển ảnh về 100x100x3
    img = tf.image.resize(img, (100,100))
    # Đưa ảnh về khoảng 0-1
    img = img / 255.0

    # Return image
    return img

def verify(model, detection_threshold, verification_threshold, verify_path):
    results = []
    input_img = preprocess(os.path.join('application_data', 'input_image', 'input_image.jpg'))
    for image in os.listdir(verify_path):
        print(image)
        validation_img = preprocess(os.path.join(verify_path, image))
        # Dự đoán
        result = model.predict(list(np.expand_dims([input_img, validation_img], axis=1)))
        results.append(result)
    
    # Ngưỡng nhận diện: Chỉ số dự đoán lớn hơn ngưỡng dự đoán 
    detection = np.sum(np.array(results) > detection_threshold)
    # Ngưỡng Verified: Tỷ lệ dự đoán ảnh đúng(positive)  / Tổng số lượng ảnh của người nhận diện (positive) 
    verification = detection / len(os.listdir(os.path.join('application_data', 'verification_images'))) 
    verified = verification > verification_threshold
    
    return results, verified

def login_check(email, image):
    verification_path = os.path.join('application_data', 'verification_images', email)
    input_path = os.path.join('application_data', 'input_image', 'input_image.jpg')
    
    header, encoded = image.split(",", 1)
    with open(input_path, "wb") as f:
        f.write(b64decode(encoded))
    
    siamese_model = tf.keras.models.load_model('models/siamesemodelv2.h5', 
                                   custom_objects={'L1Dist':L1Dist, 'BinaryCrossentropy':tf.losses.BinaryCrossentropy})
    
    try:
        try:
            results, verified = verify(siamese_model, 0.5, 0.5, verification_path)
            print(results)
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