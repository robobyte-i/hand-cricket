import cv2
import mediapipe as mp
import random
import time

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7, max_num_hands=1)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

user_score = 0
comp_score = 0
is_user_batting = None
target_score = None
comp_move = 0
user_move = 0
game_over = False
winner_text = ""
game_started = False
comp_first = False
innings = 1
last_move_time = time.time()
move_delay = 1

def count_fingers(hand_landmarks):
    fingers = [0, 0, 0, 0, 0]
    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
        fingers[0] = 1
    for i, tip in enumerate([8, 12, 16, 20]):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            fingers[i + 1] = 1
    return sum(fingers)

def draw_buttons(frame):
    cv2.rectangle(frame, (200, 300), (440, 370), (0, 255, 0), -1)
    cv2.putText(frame, "Play Again", (230, 345), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)
    cv2.rectangle(frame, (200, 400), (440, 470), (0, 0, 255), -1)
    cv2.putText(frame, "Exit", (270, 445), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)

def draw_start_buttons(frame):
    cv2.rectangle(frame, (150, 200), (300, 270), (0, 255, 255), -1)
    cv2.putText(frame, "Bat", (190, 245), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)
    cv2.rectangle(frame, (350, 200), (500, 270), (255, 0, 0), -1)
    cv2.putText(frame, "Bowl", (380, 245), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb_frame)
    fingers = 0

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            fingers = count_fingers(hand_landmarks)
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    if not game_started:
        draw_start_buttons(frame)

    if game_started and not game_over:
        current_time = time.time()
        if (current_time - last_move_time) >= move_delay and 1 <= fingers <= 5:
            last_move_time = current_time
            user_move = fingers
            comp_move = random.randint(1, 5)

            if innings == 1:
                if is_user_batting:
                    if user_move == comp_move:
                        innings = 2
                        is_user_batting = False
                        target_score = user_score + 1
                    else:
                        user_score += user_move
                else:
                    if user_move == comp_move:
                        innings = 2
                        is_user_batting = True
                        target_score = comp_score + 1
                    else:
                        comp_score += comp_move
            else:
                if is_user_batting:
                    if user_move == comp_move or user_score >= target_score:
                        game_over = True
                        winner_text = "You Win!" if user_score >= target_score else "You Lose!"
                    else:
                        user_score += user_move
                else:
                    if user_move == comp_move or comp_score >= target_score:
                        game_over = True
                        winner_text = "You Win!" if comp_score < target_score else "You Lose!"
                    else:
                        comp_score += comp_move

    if game_started:
        if is_user_batting:
            cv2.putText(frame, f"Your Score: {user_score}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        else:
            cv2.putText(frame, f"Comp Score: {comp_score}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        if target_score is not None:
            cv2.putText(frame, f"Target: {target_score}", (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        cv2.putText(frame, f"Comp: {comp_move}", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
        cv2.putText(frame, f"You: {user_move}", (500, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 165, 0), 3)

    if game_over:
        cv2.putText(frame, winner_text, (220, 250), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 0), 4)
        draw_buttons(frame)

    cv2.imshow("Hand Cricket", frame)

    def mouse_click(event, x, y, flags, param):
        global user_score, comp_score, is_user_batting, target_score, game_over, winner_text, game_started, comp_first, innings

        if event == cv2.EVENT_LBUTTONDOWN:
            if not game_started:
                if 150 <= x <= 300 and 200 <= y <= 270:
                    is_user_batting = True
                    game_started = True
                    comp_first = False
                    innings = 1
                elif 350 <= x <= 500 and 200 <= y <= 270:
                    is_user_batting = False
                    game_started = True
                    comp_first = True
                    innings = 1

            elif game_over:
                if 200 <= x <= 440 and 300 <= y <= 370:
                    user_score = 0
                    comp_score = 0
                    is_user_batting = None
                    target_score = None
                    game_over = False
                    winner_text = ""
                    game_started = False
                    comp_first = False
                    innings = 1
                elif 200 <= x <= 440 and 400 <= y <= 470:
                    cap.release()
                    cv2.destroyAllWindows()
                    exit()

    cv2.setMouseCallback("Hand Cricket", mouse_click)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
