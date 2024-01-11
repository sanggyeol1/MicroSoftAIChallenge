import numpy as np
import cv2
import os, time
import YB_Pcb_Car

car = YB_Pcb_Car.YB_Pcb_Car()

# Init camera 
cap = cv2.VideoCapture(0)
cap.set(3, 320)  # set Width
cap.set(4, 240)  # set Height

# Camera settings
cap.set(cv2.CAP_PROP_BRIGHTNESS, 55)
cap.set(cv2.CAP_PROP_CONTRAST, 55)
cap.set(cv2.CAP_PROP_SATURATION, 70)
cap.set(cv2.CAP_PROP_GAIN, 80)

t_start = time.time()
fps = 0
count = 0

def rotate_servo(servo_id, angle):
    """
    Rotate the servo motor to the specified angle.
    """
    car.Ctrl_Servo(servo_id, angle)
    time.sleep(0.05)

rotate_servo(1, 99)     #  OX / XO
rotate_servo(2, 130)

while True:
    ret, frame = cap.read()

    # Calculate FPS
    fps += 1
    mfps = fps / (time.time() - t_start)

    # Show the frame
    cv2.imshow('frame', frame)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    # cv2.imshow('gray_frame', gray_frame)

    # Check for key presses
    k = cv2.waitKey(30) & 0xff
    if k == 27:  # press 'ESC' to quit
        break

    if k == 32:  # press 'SPACE' to take a photo
        path = "./nuttttt/nut"
        print("image:{}_{}.jpg saved".format(path, str(count)))
        cv2.imwrite("{}_{}.jpg".format(path, str(count)), frame)
        # cv2.imwrite("{}_{}.jpg".format(path, str(count)), gray_frame)
        count += 1

    time.sleep(0.01)

cap.release()
cv2.destroyAllWindows()
