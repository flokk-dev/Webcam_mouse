# IMPORT: utils
import time

# IMPORT: image processing
import cv2
import mediapipe as mp

# IMPORT: mouth management
import pyautogui

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands


def get_x_position(hand_pointer, screen_width):
    min_x = 0.2
    max_x = 0.8

    x_pos = 1 - hand_pointer.x
    if min_x <= x_pos <= max_x:
        x_pos = (x_pos - min_x) / (max_x - min_x)
    elif x_pos < min_x:
        x_pos = 0
    else:
        x_pos = 1

    return x_pos * screen_width


def get_y_position(hand_pointer, screen_height):
    min_y = 0.2
    max_y = 0.8

    y_pos = hand_pointer.y
    if min_y <= y_pos <= max_y:
        y_pos = (y_pos - min_y) / (max_y - min_y)
    elif y_pos < min_y:
        y_pos = 0
    else:
        y_pos = 1

    return y_pos * screen_height


# CODE
if __name__ == "__main__":
    # LAUNCH VIDEO CAPTURE
    cap = cv2.VideoCapture(0)

    # LAUNCH HANDS DETECTION
    hands_detection = mp_hands.Hands(
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    # GET SCREEN RESOLUTION
    screen_resolution = pyautogui.size()
    screen_width, screen_height = screen_resolution.width, screen_resolution.height

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # GET A FRAME
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands_detection.process(image)

        # GET THE HAND LANDMARKS
        try:
            hand_positions = results.multi_hand_landmarks[0].landmark
        except TypeError:
            continue

        # GET THE INTERESTING LANDMARKS
        pouce = hand_positions[4]
        index = hand_positions[8]

        # MOVE THE MOUSE
        hand_pointer = hand_positions[9]
        try:
            pyautogui.moveTo(
                get_x_position(hand_pointer, screen_width),
                get_y_position(hand_pointer, screen_height),
            )
        except pyautogui.FailSafeException:
            continue

        # CLICK
        x_diff = abs(pouce.x - index.x)
        y_diff = abs(pouce.y - index.y)

        if x_diff < 0.04 and y_diff < 0.05:
            pyautogui.click()

    cap.release()
