# Importing necessary libraries
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
import cv2
import streamlit as st
import numpy as np
import uuid
import tensorflow as tf
import h5py
import io
from keras.layers import Layer


###############################################################################################
# Define a custom Keras layer for L1 distance metric
class L1Dist(Layer):
    # Constructor
    def __init__(self, **kwargs):
        super().__init__()

    # Call method for calculating L1 distance
    def call(self, input_embedding, validation_embedding):
        return tf.math.abs(input_embedding - validation_embedding)


################################################################################################
# Load Firebase credentials
cred = credentials.Certificate("key.json")

# Generate a unique app name for initializing Firebase app
app_name = f'{uuid.uuid1()}'

# Initialize Firebase app with the credentials
firebase_admin.initialize_app(cred, {'storageBucket': 'check-in-out-face-recognition.appspot.com'}, name=app_name)

# Get the default bucket
bucket = storage.bucket(app=firebase_admin.get_app(name=app_name))
################################################################################################

# Load the pre-trained model with the custom layer
test_model = tf.keras.models.load_model('siamesemodelv5.h5', custom_objects={'L1Dist': L1Dist,
                                                                             'BinaryCrossentropy': tf.losses.BinaryCrossentropy})

################################################################################################

# Get the model blob from Firebase Storage
model_blob = bucket.blob('siamesemodelv5.h5')

# Download the model bytes
file_bytes = model_blob.download_as_bytes()

# Load the model from the byte stream
with h5py.File(io.BytesIO(file_bytes), 'r') as f:
    loaded_model = tf.keras.models.load_model(f, custom_objects={'L1Dist': L1Dist,
                                                                 'BinaryCrossentropy': tf.losses.BinaryCrossentropy})


################################################################################################

def compare_images():
    """
       This function retrieves a positive image from a Firebase storage bucket, resizes and rescales it,
       compares it to all images in the same bucket except for a list of images to be skipped, using a
       pre-trained Siamese neural network model, and returns the best accuracy and the ID of the
       corresponding image. It also displays a dictionary of the prediction results for all images
       that were compared.

       Returns:
           - best_accuracy (float): the highest accuracy value among all compared images
           - best_id (str): the ID of the image with the highest accuracy value
    """
    # Download the positive image from Firebase Storage
    positive_blob = bucket.blob('anchor.jpg')
    positive_bytes = positive_blob.download_as_bytes()
    positive_np = cv2.imdecode(np.frombuffer(positive_bytes, np.uint8), -1)

    # Resize and rescale the positive image
    positive_resize = cv2.resize(positive_np, (100, 100))
    positive_rescale = positive_resize / 255.0

    # Create a dictionary to store the similarity scores
    results = {}

    # List all the files in the Firebase Storage bucket
    skip_list = ['positive.jpg', 'siamesemodelv2.h5', 'siamesemodelv3.h5', 'siamesemodelv5.h5',
                 'siamesemodelvJUPYTER.h5']
    files = bucket.list_blobs()

    # Loop through all the files in the Firebase Storage bucket
    for file in files:
        image = file.name
        if image not in skip_list:
            # Download the anchor image from Firebase Storage
            anchor_blob = bucket.blob(image)
            anchor_bytes = anchor_blob.download_as_bytes()
            anchor_np = cv2.imdecode(np.frombuffer(anchor_bytes, np.uint8), -1)

            # Resize and rescale the anchor image
            anchor_resize = cv2.resize(anchor_np, (100, 100))
            anchor_rescale = anchor_resize / 255.0

            # Predict the similarity score between the positive and anchor images using the pre-trained model
            pred = test_model.predict(list(np.expand_dims([positive_rescale, anchor_rescale], axis=1)))
            results[image.split('.')[0]] = pred[0][0]

    # Write the similarity scores to the Streamlit app
    st.write(results)

    # Find the anchor image with the highest similarity score
    best_id = max(results, key=results.get)
    best_accuracy = results[best_id]
    return best_accuracy, best_id
