import pickle
import cv2
import mediapipe as mp
import numpy as np
import subprocess  # This will be used to call the 'say' command

# Load your hand gesture recognition model
model_dict = pickle.load(open('/Users/kajalshukla/Desktop/Capstone_2/trang/Face-ASL-recognition/asl-recognition-rfm/model_both.p', 'rb'))
model = model_dict['model']

# Start video capture
cap = cv2.VideoCapture(0)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

# Label dictionary for ASL
labels_dict = {0: 'A', 1: 'B', 2: 'C',
               3: 'D', 4: 'E', 5: 'F',
               6: 'G', 7: 'H', 8: 'I',
               9: 'J', 10: 'K', 11: 'L',
               12: 'M', 13: 'N', 14: 'O', 
               15: 'P', 16: 'Q', 17: 'R', 
               18: 'S', 19: 'T', 20: 'U', 
               21: 'V', 22: 'W', 23: 'X', 
               24: 'Y', 25: 'Z'}

# Variables for gesture confirmation
confirmation_threshold = 15  # Number of frames to confirm the gesture
gesture_counter = 0
current_gesture = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    H, W, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())

            # Data preparation for the model
            data_aux = []
            x_ = []
            y_ = []

            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
    
                x_.append(x)
                y_.append(y)
    
            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                data_aux.append(x - min(x_))
                data_aux.append(y - min(y_))
    
            x1 = int(min(x_) * W) - 10
            y1 = int(min(y_) * H) - 10
    
            x2 = int(max(x_) * W) - 10
            y2 = int(max(y_) * H) - 10
    
            prediction = model.predict([np.asarray(data_aux)])
            predicted_character = labels_dict[int(prediction[0])]
            
            prediction_proba = model.predict_proba([np.asarray(data_aux)])
            prediction_proba_pct = round(max(prediction_proba[0]) * 100,2)

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 4)
            cv2.putText(frame, 
                        f"{predicted_character} - {prediction_proba_pct}%", 
                        (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        1.3, (0, 0, 0), 3,
                        cv2.LINE_AA)
            
            # Confirmation process
            if predicted_character == current_gesture:
                gesture_counter += 1
                if gesture_counter == confirmation_threshold:
                    # Speak the character out loud if confirmation threshold is reached
                    subprocess.run(['say', predicted_character], check=True)
                    gesture_counter = 0  # Reset counter after speaking
            else:
                # Reset counter if gesture changes
                current_gesture = predicted_character
                gesture_counter = 0

    # Display the frame
    cv2.imshow('frame', frame)

    # Exit loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
