import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
import cv2
import streamlit as st
import numpy as np
import uuid
import tensorflow as tf
from tensorflow import keras
import h5py
import io
###############################################################################################
# Siamese L1 Distance class
from keras.layers import Layer
class L1Dist(Layer):

    # Init method - inheritance
    def __init__(self, **kwargs):
        super().__init__()

    # Magic happens here - similarity calculation
    def call(self, input_embedding, validation_embedding):
        return tf.math.abs(input_embedding - validation_embedding)

################################################################################################
# Initialize Firebase credentials
cred = credentials.Certificate("key.json")
app_name =f'{uuid.uuid1()}'
firebase_admin.initialize_app(cred,{'storageBucket': 'check-in-out-face-recognition.appspot.com'},name=app_name)
bucket = storage.bucket(app=firebase_admin.get_app(name=app_name))
################################################################################################
test_model = tf.keras.models.load_model('siamesemodelv5.h5', custom_objects={'L1Dist':L1Dist, 'BinaryCrossentropy':tf.losses.BinaryCrossentropy})
################################################################################################
# model_blob = bucket.blob('siamesemodelv5.h5')
# file_bytes = model_blob.download_as_bytes()
# with h5py.File(io.BytesIO(file_bytes), 'r') as f:
#     loaded_model = tf.keras.models.load_model(f, custom_objects={'L1Dist':L1Dist, 'BinaryCrossentropy':tf.losses.BinaryCrossentropy})
################################################################################################

def compare_images():
    # Get images from Firebase Storage
    positive_blob = bucket.blob('positive.jpg')

    # Download image data to memory as bytes
    positive_bytes = positive_blob.download_as_bytes()

    # Convert image data to numpy arrays
    positive_np = cv2.imdecode(np.frombuffer(positive_bytes, np.uint8), -1)

    # Resize the images
    positive_resize = cv2.resize(positive_np, (100, 100))

    # Rescale the images
    positive_rescale = positive_resize/255.0

    # Display the images in Streamlit
    # st.image(image1_np, caption='Image 1', use_column_width=True)
    results={}
    skip_list=['positive.jpg','siamesemodelv2.h5','siamesemodelv3.h5','siamesemodelv5.h5','siamesemodelvJUPYTER.h5']
    files = bucket.list_blobs()
    for file in files:
        image = file.name
        if image not in skip_list:
            anchor_blob = bucket.blob(image)
            anchor_bytes = anchor_blob.download_as_bytes()
            anchor_np = cv2.imdecode(np.frombuffer(anchor_bytes, np.uint8), -1)
            anchor_resize = cv2.resize(anchor_np, (100, 100))
            anchor_rescale = anchor_resize / 255.0
            pred=test_model.predict(list(np.expand_dims([positive_rescale, anchor_rescale], axis=1)))
            results[image.split('.')[0]]=pred[0][0]
    st.write(results)
    best_id= max(results, key=results.get)
    best_accuracy=results[best_id]
    # st.write(best_accuracy)
    # st.write(best_id)
    return best_accuracy,best_id
