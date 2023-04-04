import pyrebase
import streamlit as st
import datetime
from model import compare_images

firebaseConfig = {
  'apiKey': "AIzaSyAoncHqBd3SAxCRaYYgWkPIACbbLLrN2T8",
  'authDomain': "check-in-out-face-recognition.firebaseapp.com",
  'databaseURL': "https://check-in-out-face-recognition-default-rtdb.firebaseio.com",
  'projectId': "check-in-out-face-recognition",
  'storageBucket': "check-in-out-face-recognition.appspot.com",
  'messagingSenderId': "149616764190",
  'appId': "1:149616764190:web:0c10c777b99f30a1b1550f",
  'measurementId': "G-EPE6JX5L02"
}
firebase=pyrebase.initialize_app(firebaseConfig)
auth=firebase.auth()

# Database
db = firebase.database()
storage = firebase.storage()
choice_block = st.empty()
choice = choice_block.radio('Check in/out', ['Check in/out', 'Sign up'])

employees = {}

if choice == 'Check in/out':
    image = st.camera_input(label="Check in/out")

    if image:
        storage.child('positive.jpg').put(image.getbuffer())

###########################################################################################################################################
        best_accuracy,best_id=compare_images()
        name = db.child(employees).child(str(best_id)).child("Name").get().val()
        now = datetime.datetime.now()
        check=db.child(employees).child(str(best_id)).child("check").get().val()
        report=db.child(employees).child(str(best_id)).child("report").get().val()
        Last_attendance_time=db.child(employees).child(str(best_id)).child("Last_attendance_time").get().val()
        if check=='out':
            db.child(employees).child(best_id).child("check").set("in")
            st.info(f"Hi {name}...")
            now = now.strftime('%Y-%m-%d %H:%M:%S')
            db.child(employees).child(best_id).child("Last_attendance_time").set(now)
            report[now]='in'
            db.child(employees).child(best_id).child("report").set(report)


        else:
            db.child(employees).child(best_id).child("check").set("out")
            Last_attendance_time=datetime.datetime.strptime(Last_attendance_time, '%Y-%m-%d %H:%M:%S')
            total_hours=now-Last_attendance_time
            total_hours=total_hours.total_seconds()
            total_hours = float(total_hours/3600)
            db.child(employees).child(best_id).child("Total_hours").set(total_hours)
            now = now.strftime('%Y-%m-%d %H:%M:%S')
            db.child(employees).child(best_id).child("Last_attendance_time").set(now)
            report[now] = 'out'
            db.child(employees).child(best_id).child("report").set(report)
            st.info(f"Thanks {name}, you ended your work at: {now}")
            st.info(f"You worked (total_hours) hours for this month")
###########################################################################################################################################

###########################################################################################################################################
# Sign up block
if choice == 'Sign up':
    work_id_block = st.empty()
    work_id = work_id_block.text_input('Please input your WORK ID', value='0000')

    name_block = st.empty()
    name = name_block.text_input('Please input your WORK ID', value='NAME')

    image = st.camera_input(label="Take 15 photos for your face from different angles:")

    now=datetime.datetime.now()
    now = now.strftime('%Y-%m-%d %H:%M:%S')

    report = {}
    report[now] = 'registered'

    sign_up_block = st.empty()
    sign_up = sign_up_block.button('Sign Up')
    ##################################################################################################

    ##################################################################################################

    if sign_up:
        if image:
            # storage.child(work_id).child(f'{uuid.uuid1()}').put(image.getbuffer())
            storage.child(f'{work_id}.jpg').put(image.getbuffer())
            try:
                db.child(employees).child(work_id).child("Name").set(name)
                db.child(employees).child(work_id).child("Work ID").set(work_id)
                db.child(employees).child(work_id).child("Total_hours").set(0)
                db.child(employees).child(work_id).child("Last_attendance_time").set(now)
                db.child(employees).child(work_id).child("check").set("out")
                db.child(employees).child(work_id).child("report").set(report)

                st.info(f"Welcome {name}, you can now use the system.")
                sign_up_block.empty()

            except:
                st.error('Account already exists!')
        else:
            st.error("No image captured.")

