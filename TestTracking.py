import cv2
import mediapipe as mp
import numpy

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

lip_nodes = set()
for connection in mp_face_mesh.FACEMESH_LIPS:
    lip_nodes.add(connection[0])
    lip_nodes.add(connection[1])


def distance_between(a,b):
    a = numpy.array([a.x,a.y,a.z])
    b = numpy.array([b.x,b.y,b.z])
    dist = a-b

    return numpy.sqrt(sum(dist*dist))




def get_finger_vectors(hand):
    landmarks = hand.landmark


# For webcam input:
cap = cv2.VideoCapture(1)
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
            if hand_results.multi_hand_landmarks:
                wrist = hand_results.multi_hand_world_landmarks[0].landmark[0]
                finger = hand_results.multi_hand_world_landmarks[0].landmark[9]
                lencm = distance_between(wrist, finger)*100

                wrist = hand_results.multi_hand_landmarks[0].landmark[0]
                finger = hand_results.multi_hand_landmarks[0].landmark[9]
                lenunit = distance_between(wrist, finger)



                conv_factor = lenunit/lencm

                cv2.putText(image, f"Convertion factor{conv_factor}", (10, 200), font, font_scale, font_color, thickness=2, lineType=line_type)

                if distance_between(hand_landmarks.landmark[4],hand_landmarks.landmark[8]) < 4*conv_factor:
                    cv2.putText(image, "Click", (10, 50), font, font_scale, font_color, thickness=2, lineType=line_type)
                if face_results.multi_face_landmarks:
                    finger_pos = hand_results.multi_hand_landmarks[0].landmark[8]
                    for i in lip_nodes:
                        lip_pos = face_results.multi_face_landmarks[0].landmark[i]
                        if distance_between(finger_pos, lip_pos) < 5*conv_factor:
                            cv2.putText(image, "SPEAK", (10, 150), font, font_scale, font_color, thickness=2, lineType=line_type)
                            
            
            cv2.imshow('MediaPipe Hands', image)

            if cv2.waitKey(5) & 0xFF == 27:
                break

cap.release()
