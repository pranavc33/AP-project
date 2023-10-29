import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import pickle
from landmarks import landmarks
import sys
sys.path.insert(0, "E:\AP")
  # You should have the landmarks defined
import time

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Load the pre-trained model
with open('E:\AP\deadlift.pkl', 'rb') as f:
    model = pickle.load(f)

st.set_page_config(page_title="LIVE VIDEO", layout="wide")
st.title("DEADLIFT COUNTER")

# Create placeholders for the video and text
video_placeholder = st.empty()
stage_text = st.empty()
reps_text = st.empty()
prob_text = st.empty()

cap = cv2.VideoCapture(0)
pose = mp_pose.Pose(min_tracking_confidence=0.5, min_detection_confidence=0.5)

current_stage = ""
counter = 0
bodylang_prob = np.array([0, 0])
bodylang_class = ""

def reset_counter():
    global counter
    counter = 0

if "counter" not in st.session_state:
    st.session_state.counter = 0

if "current_stage" not in st.session_state:
    st.session_state.current_stage = "up"

while True:
    ret, frame = cap.read()
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image)
    mp_drawing.draw_landmarks(
        image,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        mp_drawing.DrawingSpec(color=(106, 13, 173), thickness=4, circle_radius=5),
        mp_drawing.DrawingSpec(color=(255, 102, 0), thickness=5, circle_radius=10),
    )

    try:
        row = np.array(
            [[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]
        ).flatten()
        X = pd.DataFrame([row], columns=landmarks)
        bodylang_prob = model.predict_proba(X)[0]
        bodylang_class = model.predict(X)[0]

        if bodylang_class == "down" and bodylang_prob[bodylang_prob.argmax()] > 0.7:
            st.session_state.current_stage = "down"
        elif st.session_state.current_stage == "down" and bodylang_class == "up" and bodylang_prob[bodylang_prob.argmax()] > 0.7:
            st.session_state.current_stage = "up"
            st.session_state.counter += 1

    except Exception as e:
        print(e)

    counter = st.session_state.counter
    prob = bodylang_prob[bodylang_prob.argmax()]
    stage = st.session_state.current_stage

    # Update the Streamlit components with the latest values
    video_placeholder.image(image, channels="RGB")
    stage_text.text(f"STAGE: {stage}")
    reps_text.text(f"REPS: {counter}")
    prob_text.text(f"PROB: {prob}")

    time.sleep(0.1)  # Adjust the delay to control the frame rate
