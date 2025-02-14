import cv2
import mediapipe as mp

def count_fingers(hand_landmarks):
    fingers = [0, 0, 0, 0, 0]  # Thumb, Index, Middle, Ring, Pinky
    
    # Thumb (Check x position instead of y for left/right distinction)
    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
        fingers[0] = 1
    
    # Other fingers (Check if tip is above PIP joint in y-axis)
    for i, tip in enumerate([8, 12, 16, 20]):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            fingers[i + 1] = 1
    
    return sum(fingers)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Start Video Capture
cap = cv2.VideoCapture(0)
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break
    
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            fingers_count = count_fingers(hand_landmarks)
            cv2.putText(frame, f'Fingers: {fingers_count}', (50, 100), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imshow('Hand Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
