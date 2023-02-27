import cv2
import mediapipe as mp
import numpy as np
import time
import os
from gestures import Gestures
from finger_angles import hand_curl_vals
from mouse_move import move_mouse
from text import draw_text
from points import point, distance_between, get_ratio_point, get_hand_vel



###########################################################################################
# TODO:
# Click and drag
# Nice UI, Tells you controlls and what it's doing
# Calibration Sudgestions
# point at ear and scroll to change volume
###########################################################################################

thresholds = [1.2,1.1,1.1,1.1,1.1]
max_mem = 10

if os.getlogin() == "surface":
    cam_to_use = 1
else:
    cam_to_use = 0

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh

g = Gestures()

# Get list of all nodes in the lips
lip_nodes = set()
for connection in mp_face_mesh.FACEMESH_LIPS:
    lip_nodes.add(connection[0])
    lip_nodes.add(connection[1])

# For webcam input:
cap = cv2.VideoCapture(cam_to_use)
cap.set(cv2.CAP_PROP_FPS, 60)

# Calculate the aspect ratio
aspect_ratio = cap.get(cv2.CAP_PROP_FRAME_WIDTH) / cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

last = time.time()
hand_pos = []
hand_vel = []
finger_curl = []
finger_up = []
face_hist = []
speaking = False
with mp_hands.Hands(max_num_hands=1,model_complexity=0,min_detection_confidence=0.5,min_tracking_confidence=0.5) as hands:
    with mp_face_mesh.FaceMesh(max_num_faces=1,refine_landmarks=True,min_detection_confidence=0.5,min_tracking_confidence=0.5) as face_mesh:
        
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            hand_results = hands.process(image)
            face_results = face_mesh.process(image)

            # Draw the hand annotations on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if hand_results.multi_hand_landmarks:
                for hand_landmarks in hand_results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(image,hand_landmarks,mp_hands.HAND_CONNECTIONS,mp_drawing_styles.get_default_hand_landmarks_style(),mp_drawing_styles.get_default_hand_connections_style())

            # Draw the face mesh annotations on the image.
            if face_results.multi_face_landmarks:
                for face_landmarks in face_results.multi_face_landmarks:
                    mp_drawing.draw_landmarks(image=image,landmark_list=face_landmarks,connections=mp_face_mesh.FACEMESH_TESSELATION,landmark_drawing_spec=None,connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style())
                    mp_drawing.draw_landmarks(image=image,landmark_list=face_landmarks,connections=mp_face_mesh.FACEMESH_CONTOURS,landmark_drawing_spec=None,connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style())
                    mp_drawing.draw_landmarks(image=image,landmark_list=face_landmarks,connections=mp_face_mesh.FACEMESH_IRISES,landmark_drawing_spec=None,connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_iris_connections_style())
            # Flip the image horizontally for a selfie-view display.
            image = cv2.flip(image, 1)
            
            if hand_results.multi_hand_landmarks:
                hand = hand_results.multi_hand_landmarks[0].landmark
                hand_metric = hand_results.multi_hand_world_landmarks[0].landmark
                # Get space convertion factor
                lencm = distance_between(hand_metric[0], hand_metric[9])*100
                lenunit = distance_between(hand[0], hand[9])
                conv_factor = lenunit/lencm

                # Finger curls
                curls = hand_curl_vals(hand)
                ups = []
                for i in range(5):
                    ups.append(curls[i]<thresholds[i])
                #draw_text(image, str(ups), (10, 350))
                
                # Face gestures
                touching_mouth = False
                if face_results.multi_face_landmarks:
                    face = face_results.multi_face_landmarks[0].landmark
                    for i in lip_nodes:
                        if distance_between(hand[8], face[i]) < 8*conv_factor:
                            touching_mouth = True
                            break

                # Get data ready
                hand_pos.append(hand)
                finger_curl.append(curls)
                finger_up.append(ups)
                hand_vel.append(get_hand_vel(hand_pos))
                face_hist.append(touching_mouth)

                if len(hand_pos) > max_mem:
                    hand_pos = hand_pos[1:]
                    finger_curl = finger_curl[1:]
                    finger_up = finger_up[1:]
                    hand_vel = hand_vel[1:]
                    face_hist = face_hist[1:]
                
                if len(hand_pos) > 1:
                    g.pass_data(hand_pos, hand_vel, finger_curl, finger_up, conv_factor, face_hist)
                    g.run_all()
                                
            
            cv2.imshow('MediaPipe Hands', image)

            # Press Escape to exit
            if cv2.waitKey(5) & 0xFF == 113:
                break

cap.release()
