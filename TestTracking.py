import cv2
import mediapipe as mp
import numpy as np
import keyboard
import speech_recognition as sr
import time
import mouse
import numpy as np
import pyautogui as pagui

###########################################################################################
# TODO:
# function to get handspan (calibration function) -> used in distance function
# function to determine which fingers are closed
# function to determine direction and speed of motion of hand?
# Design gesture library
# functions to move mouse, interact with screen
###########################################################################################

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh


# Define the font properties
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 1
font_color = (255, 150, 0)
line_type = cv2.LINE_AA

speaking = False
speaking_end = lambda wait_for_stop=False: ""
speaking_timeout = 1
last_spoke = time.time()
r = sr.Recognizer()
m = sr.Microphone()
with m as source:
    r.adjust_for_ambient_noise(source)  # we only need to calibrate once, before we start listening


width, height = pagui.size()

def move_mouse(old_pos_hand, new_pos_hand):

    old_pos_mouse = [old_pos_hand.x * width, old_pos_hand.y*height]
    new_pos_mouse = [new_pos_hand.x * width, new_pos_hand.y*height]

    move_vect = [new_pos_mouse[0] - old_pos_mouse[0], new_pos_mouse[1] - old_pos_mouse[1]]
    mouse.move(move_vect[0], -move_vect[1], False)

# Class to hold a point
class point():
    def __init__(self, x,y,z):
        self.x = x
        self.y = y
        self.z = z

# this is called from the background thread
def callback(recognizer, audio):
    print("AUDIO HAS CALLBACKED")
    # received audio data, now we'll recognize it using Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        words = recognizer.recognize_google(audio)
        print("Google Speech Recognition thinks you said " + words)
        keyboard.write(words)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

# Get list of all nodes in the lips
lip_nodes = set()
for connection in mp_face_mesh.FACEMESH_LIPS:
    lip_nodes.add(connection[0])
    lip_nodes.add(connection[1])


# get distance between 2 points
def distance_between(a,b):
    a = np.array([a.x,a.y,a.z])
    b = np.array([b.x,b.y,b.z])
    dist = a-b

    return np.sqrt(sum(dist*dist))

def get_ratio_point(pos, ratio):
    return point(pos.x, pos.y*ratio, pos.z)

# For webcam input:
cap = cv2.VideoCapture(1)

# Get the current frame width and height
frame_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

# Calculate the aspect ratio
aspect_ratio = frame_width / frame_height

last = time.time()
old_finger = point(0,0,0)
with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
    
    with mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as face_mesh:
        
        while cap.isOpened():
            delta = last - time.time()
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                continue

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            hand_results = hands.process(image)
            face_results = face_mesh.process(image)

            # Draw the hand annotations on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if hand_results.multi_hand_landmarks:
                for hand_landmarks in hand_results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style()
                    )

            # Draw the face mesh annotations on the image.
            if face_results.multi_face_landmarks:
                for face_landmarks in face_results.multi_face_landmarks:
                    mp_drawing.draw_landmarks(
                        image=image,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_TESSELATION,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing_styles
                        .get_default_face_mesh_tesselation_style())
                    mp_drawing.draw_landmarks(
                        image=image,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_CONTOURS,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing_styles
                        .get_default_face_mesh_contours_style())
                    mp_drawing.draw_landmarks(
                        image=image,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_IRISES,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing_styles
                        .get_default_face_mesh_iris_connections_style())
            # Flip the image horizontally for a selfie-view display.
            image = cv2.flip(image, 1)
            
            touching_mouth = False
            if hand_results.multi_hand_landmarks:
                lencm = distance_between(
                    hand_results.multi_hand_world_landmarks[0].landmark[0], 
                    hand_results.multi_hand_world_landmarks[0].landmark[9])*100
                lenunit = distance_between(
                    hand_results.multi_hand_landmarks[0].landmark[0], 
                    hand_results.multi_hand_landmarks[0].landmark[9])
                conv_factor = lenunit/lencm

                touch_point = hand_results.multi_hand_landmarks[0].landmark[5]

                # Check click
                if distance_between(hand_landmarks.landmark[4],hand_landmarks.landmark[8]) < 4*conv_factor:
                    move_mouse(old_finger, touch_point)
                    cv2.putText(image, "Click", (10, 50), font, font_scale, font_color, thickness=2, lineType=line_type)

                old_finger = touch_point
                
                # Touch face
                if face_results.multi_face_landmarks:
                    finger_pos = hand_results.multi_hand_landmarks[0].landmark[8]
                    for i in lip_nodes:
                        lip_pos = face_results.multi_face_landmarks[0].landmark[i]
                        if distance_between(finger_pos, lip_pos) < 5*conv_factor:
                            touching_mouth = True
                            break
                    

            if touching_mouth:
                cv2.putText(image, "SPEAK", (10, 150), font, font_scale, font_color, thickness=2, lineType=line_type)
                if not speaking and time.time() - last_spoke > speaking_timeout:
                    speaking = True
                    speaking_end = r.listen_in_background(m, callback)
                    print("listening")
            else:
                if speaking:
                    last_spoke = time.time()
                    speaking = False
                    speaking_end(wait_for_stop=False)
                    print("stopped speaking")
                                
            
            cv2.imshow('MediaPipe Hands', image)

            if cv2.waitKey(5) & 0xFF == 27:
                break

cap.release()
