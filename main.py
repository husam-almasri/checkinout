# Importing necessary libraries
import pyrebase
import streamlit as st
import datetime
from model import compare_images

# A Firebase configuration object that contains various API keys and project IDs that are required to connect to a Firebase project.
firebaseConfig = {
# apiKey: This is the API key that is used to authenticate requests made from the client-side (e.g., a web application or a mobile app) to the Firebase project.
  'apiKey': "AIzaSyAoncHqBd3SAxCRaYYgWkPIACbbLLrN2T8",
# authDomain: This is the domain name that Firebase uses for authentication. This domain name is used to redirect users to the Firebase authentication page when they sign in or sign up for an account.
  'authDomain': "check-in-out-face-recognition.firebaseapp.com",
# databaseURL: This is the URL of the Firebase Realtime Database. It is used to establish a connection between the client and the Firebase database.
  'databaseURL': "https://check-in-out-face-recognition-default-rtdb.firebaseio.com",
# projectId: This is the ID of the Firebase project. It is used to identify the project in the Firebase console.
  'projectId': "check-in-out-face-recognition",
# storageBucket: This is the name of the Google Cloud Storage bucket associated with the Firebase project. It is used to store files and other data that are used in the Firebase project.
  'storageBucket': "check-in-out-face-recognition.appspot.com",
# messagingSenderId: This is the ID of the Firebase Cloud Messaging sender. It is used to send push notifications to users in the Firebase project.
  'messagingSenderId': "149616764190",
# appId: This is the ID of the Firebase app. It is used to identify the app in the Firebase console.
  'appId': "1:149616764190:web:0c10c777b99f30a1b1550f",
# measurementId: This is the ID of the Firebase Analytics measurement. It is used to collect and analyze user behavior data in the Firebase project.
  'measurementId': "G-EPE6JX5L02"
}

# Initialize Firebase app with config
firebase=pyrebase.initialize_app(firebaseConfig)
# Initialize Firebase auth
auth=firebase.auth()

# Initialize Firebase database
db = firebase.database()
# Initialize Firebase storage
storage = firebase.storage()

# Create an empty Streamlit block
choice_block = st.empty()
# Create a Streamlit radio button for user choice
choice = choice_block.radio('Check in/out', ['Check in/out', 'Sign up'])

# Create an empty dictionary for the employees' data
employees = {}

# Check if the user selected the 'Check in/out' option
if choice == 'Check in/out':
    # Capture an image using the camera
    image = st.camera_input(label="Check in/out")

    # If an image was captured
    if image:

        # Upload the image to a storage service
        storage.child('anchor.jpg').put(image.getbuffer())

        # Compare the captured image with the registered employees' images to find the best match
        best_accuracy, best_id = compare_images()

        # Retrieve the name of the matched employee from the database
        name = db.child(employees).child(str(best_id)).child("Name").get().val()

        # Get the current date and time
        now = datetime.datetime.now()

        # Get the check status of the matched employee from the database
        check = db.child(employees).child(str(best_id)).child("check").get().val()

        # Get the attendance report of the matched employee from the database
        report = db.child(employees).child(str(best_id)).child("report").get().val()

        # Get the last attendance time of the matched employee from the database
        Last_attendance_time = db.child(employees).child(str(best_id)).child("Last_attendance_time").get().val()

        # If the matched employee is checked out
        if check == 'out':

            # Set the check status of the matched employee to 'in'
            db.child(employees).child(best_id).child("check").set("in")

            # Show a farewell message to the matched employee, along with their check-in
            st.info(f"Welcome {name}, you checked in at: {now}")

            # Convert the current date and time to a string in a specified format
            now = now.strftime('%Y-%m-%d %H:%M:%S')

            # Set the last attendance time of the matched employee to the current time
            db.child(employees).child(best_id).child("Last_attendance_time").set(now)

            # Update the attendance report of the matched employee to indicate that they checked in at the current time
            report[now] = 'in'
            db.child(employees).child(best_id).child("report").set(report)

        # If the matched employee is checked in
        else:

            # Set the check status of the matched employee to 'out'
            db.child(employees).child(best_id).child("check").set("out")

            # Convert the last attendance time of the matched employee from a string to a datetime object
            Last_attendance_time = datetime.datetime.strptime(Last_attendance_time, '%Y-%m-%d %H:%M:%S')

            # Calculate the total hours worked by the matched employee since their last check-in
            total_hours = now - Last_attendance_time
            total_hours = total_hours.total_seconds()
            total_hours = float(total_hours / 3600)
            total_hours = round(total_hours, 2)

            # Update the total hours worked by the matched employee in the database
            db.child(employees).child(best_id).child("Total_hours").set(total_hours)

            # Convert the current date and time to a string in a specified format
            now = now.strftime('%Y-%m-%d %H:%M:%S')

            # Set the last attendance time of the matched employee to the current time
            db.child(employees).child(best_id).child("Last_attendance_time").set(now)

            # Update the attendance report of the matched employee to indicate that they checked out at the current time
            report[now] = 'out'
            db.child(employees).child(best_id).child("report").set(report)

            # Show a farewell message to the matched employee, along with their check-out
            st.info(f"Thanks {name}, you checked out at: {now}")
            # Displaying information to the user about the number of hours they worked during the current month.
            st.info(f"You worked ({total_hours}) hours for this month")

# Check if the user selected the 'Sign up' option
if choice == 'Sign up':

    # Take input for work ID
    work_id_block = st.empty()
    work_id = work_id_block.text_input('Please input your WORK ID', value='0000')
    # Take input for name
    name_block = st.empty()
    name = name_block.text_input('Please input your NAME', value='NAME')

    # Capture 15 photos for face recognition
    image = st.camera_input(label="Take 15 photos for your face from different angles:")

    # Get current time
    now = datetime.datetime.now()
    now = now.strftime('%Y-%m-%d %H:%M:%S')

    # Create initial report with 'registered' status
    report = {}
    report[now] = 'registered'

    # Display a button for sign up
    sign_up_block = st.empty()
    sign_up = sign_up_block.button('Sign Up')

    # Execute on button click
    if sign_up:
        # Check if image is captured
        if image:
            # Upload the image to the storage
            storage.child(f'{work_id}.jpg').put(image.getbuffer())

            # Set user data in the database
            try:
                # Set the name for the new employee
                db.child(employees).child(work_id).child("Name").set(name)

                # Set the work ID for the new employee
                db.child(employees).child(work_id).child("Work ID").set(work_id)

                # Set the initial total hours worked for the new employee to 0
                db.child(employees).child(work_id).child("Total_hours").set(0)

                # Set the last attendance time for the new employee to the current time
                db.child(employees).child(work_id).child("Last_attendance_time").set(now)

                # Set the initial check status for the new employee to "out"
                db.child(employees).child(work_id).child("check").set("out")

                # Set the attendance report for the new employee
                db.child(employees).child(work_id).child("report").set(report)

                # Show success message
                st.info(f"Welcome {name}, you can now use the system.")
                sign_up_block.empty()

            except:
                # Show error message if the account already exists
                st.error('Account already exists!')
        else:
            # Show error message if no image is captured
            st.error("No image captured.")
