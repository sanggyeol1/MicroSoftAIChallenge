import cv2
import numpy as np
import RPi.GPIO as GPIO
import YB_Pcb_Car
import threading
import time
import random

# Camera and car initialization
cap = cv2.VideoCapture(0)
cap.set(3, 320)  # Set width
cap.set(4, 240)  # Set height
cap.set(cv2.CAP_PROP_BRIGHTNESS, 37)
cap.set(cv2.CAP_PROP_CONTRAST, 37)
cap.set(cv2.CAP_PROP_SATURATION, 20)
cap.set(cv2.CAP_PROP_GAIN, 20)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
cap.set(cv2.CAP_PROP_EXPOSURE , 450)

car = YB_Pcb_Car.YB_Pcb_Car()

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(32, GPIO.OUT)

p = GPIO.PWM(32, 220)

AvoidSensorLeft = 21     #Left infrared obstacle avoidance sensor pin
AvoidSensorRight = 19    #Right infrared obstacle avoidance sensor pin
Avoid_ON = 22   #Infrared obstacle avoidance sensor switch pin

GPIO.setup(AvoidSensorLeft,GPIO.IN)
GPIO.setup(AvoidSensorRight,GPIO.IN)
GPIO.setup(Avoid_ON,GPIO.OUT)
GPIO.output(Avoid_ON,GPIO.HIGH)

# Constants
MOTOR_UP_SPEED = 50    # Speed range: 65 ~ 125 45
MOTOR_DOWN_SPEED = 35   # 25- 30
DETECT_VALUE = 50        # real 20 / test 50

# Haar Cascade models
ox_cascade = cv2.CascadeClassifier('cascade_ox2.xml')    # OX
xo_cascade = cv2.CascadeClassifier('cascade_xo2.xml')    # XO
traffic_light_cascade = cv2.CascadeClassifier('cascade_traf.xml') # Traffic LIght
red_light_cadcade = cv2.CascadeClassifier('cascade_red_3.xml')    # RED Light

# Detection functions
def detect_ox(frame, control_signals):
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    ox = ox_cascade.detectMultiScale(frame, scaleFactor=1.1, minNeighbors=3)
    # ox = ox_cascade.detectMultiScale(frame)
    if not len(ox) : 
        return
    for (x, y, w, h) in ox:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
    control_signals['ox'] = len(ox) > 0

def detect_xo(frame, control_signals):
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    xo = xo_cascade.detectMultiScale(frame, scaleFactor=1.1, minNeighbors=3)
    # xo = xo_cascade.detectMultiScale(gray)
    if not len(xo) : 
        return
    for (x, y, w, h) in xo:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
    control_signals['xo'] = len(xo) > 0

def detect_traffic_light(frame, control_signals):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # traffic_lights = traffic_light_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=2)
    traffic_lights = traffic_light_cascade.detectMultiScale(frame)
    if not len(traffic_lights) : 
        return
    for (x, y, w, h) in traffic_lights:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
    control_signals['traffic_light'] = len(traffic_lights) > 0

def detect_red_light(frame, control_signals):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # red_lights = red_light_cadcade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3)
    red_lights = red_light_cadcade.detectMultiScale(frame)
    if not len(red_lights) : 
        return
    for (x, y, w, h) in red_lights:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    control_signals['red_light'] = len(red_lights) > 0

# Autonomous driving functions 
def process_frame(frame):
    pts_src = np.float32([[10, 240], [310, 240], [310, 180], [10,180]])
    # pts_src = np.float32([[0, 240], [300, 240], [300, 180], [0,180]])    # M
    pts_dst = np.float32([[0, 240], [320, 240], [320, 0], [0, 0]])

    # 사각형 그리기
    pts = pts_src.reshape((-1, 1, 2)).astype(np.int32)  # np.float32에서 np.int32로 변경
    frame = cv2.polylines(frame, [pts], isClosed=True, color=(0, 0, 255), thickness=None)
    # cv2.imshow('startchFrame', frame)

    # Stratch Road cut
    mat_affine = cv2.getPerspectiveTransform(pts_src, pts_dst)
    frame_transformed = cv2.warpPerspective(frame, mat_affine, (320, 240))
    # cv2.imshow('frame_startch', frame_transformed)

    # Convert to grayscale and apply binary threshold
    gray_frame = cv2.cvtColor(frame_transformed, cv2.COLOR_RGB2GRAY)
    # cv2.imshow('3_gray_frame', gray_frame)
    _, binary_frame = cv2.threshold(gray_frame, DETECT_VALUE, 255, cv2.THRESH_BINARY)
    return binary_frame

def parking_frame(frame):
    pts_park = np.float32([[10, 180], [310, 180], [310, 120], [10, 120]])
    # pts_park = np.float32([[0, 220], [320, 220], [320, 160], [0, 160]])
    pts_dst = np.float32([[0, 240], [320, 240], [320, 0], [0, 0]])
    pts = pts_park.reshape((-1, 1, 2)).astype(np.int32)
    frame = cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 255), thickness=1)

    # Stratch Parking lot cut
    mat_affine_2 = cv2.getPerspectiveTransform(pts_park, pts_dst)
    frame_transformed_2 = cv2.warpPerspective(frame, mat_affine_2, (320, 240))
    cv2.imshow('frame_startch2', frame_transformed_2)
    return frame_transformed_2

def decide_direction(histogram):
    left = int(np.sum(histogram[:int(len(histogram) / 4)]))
    right = int(np.sum(histogram[int(3 * len(histogram) / 4):]))
    up = np.sum(histogram[int(len(histogram) / 4):int(3 * len(histogram) / 4)])

    print("Left:", left, end=' ')
    print("Right:", right, end=' ')
    print("Straight:", up)

    if abs(right - left) > 400000:
        return "LEFT" if right > left else "RIGHT"
    elif up < 100000:
        return "UP"
    else:
        return "UP"

def control_car(direction):
    print(f"Controlling car: {direction}")
    if direction == "UP":
        rotate_servo(1, 99)
        car.Car_Run(MOTOR_UP_SPEED -5 , MOTOR_UP_SPEED -5)
    elif direction == "LEFT":
        rotate_servo(1, 112)
        car.Car_Left(MOTOR_DOWN_SPEED, MOTOR_UP_SPEED)
    elif direction == "RIGHT":
        rotate_servo(1, 86) # normally -17 new -12
        car.Car_Right(MOTOR_UP_SPEED, MOTOR_DOWN_SPEED)
    elif direction == "RANDOM":
        rotate_servo(1, 99)
        random_direction = random.choice(["LEFT", "RIGHT"])
        control_car(random_direction)

# Parking system
def ox():
    print(' - OX - ')
    car.Car_Left(MOTOR_DOWN_SPEED, MOTOR_UP_SPEED)
    time.sleep(1)
    car.Car_Run(MOTOR_UP_SPEED - 10, MOTOR_UP_SPEED - 10)
    time.sleep(1.5)
    car.Car_Right(MOTOR_UP_SPEED, MOTOR_DOWN_SPEED)
    time.sleep(1.5)
    car.Car_Run(MOTOR_UP_SPEED - 10, MOTOR_UP_SPEED - 10)
    time.sleep(1.5)
    car.Car_Stop
    # time.sleep(1)

def xo():
    print(' - XO - ')
    car.Car_Right(MOTOR_UP_SPEED, MOTOR_DOWN_SPEED)
    time.sleep(1.5)
    # car.Car_Run(MOTOR_UP_SPEED - 10, MOTOR_UP_SPEED - 10)
    # time.sleep(1)
    car.Car_Left(MOTOR_DOWN_SPEED, MOTOR_UP_SPEED)
    time.sleep(1)
    car.Car_Run(MOTOR_UP_SPEED - 10, MOTOR_UP_SPEED - 10)
    time.sleep(1.5)
    car.Car_Stop
    # time.sleep(1)

# camera servo
def rotate_servo(servo_id, angle):
    car.Ctrl_Servo(servo_id, angle)
    # time.sleep(0.05)

# Main loop
try:
    rotate_servo(1, 99)  # Rotate servo at S1 to 90 degrees 좌우 99
    rotate_servo(2, 117)  #117
    val = 0
    signal = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame from camera.")
            break
        # frame = auto_adjust_brightness_contrast(frame)

        # Frame for Parking lot
        Park_frame = parking_frame(frame)

        LeftSensorValue  = GPIO.input(AvoidSensorLeft)
        RightSensorValue = GPIO.input(AvoidSensorRight)

        # Shared control signals dictionary
        control_signals = {'ox': False, 'xo': False, 'traffic_light': False, 'red_light': False}

        # Create and start threads for detection tasks
        try:
            ox_thread = threading.Thread(target=detect_ox, args=(Park_frame.copy(), control_signals))
            xo_thread = threading.Thread(target=detect_xo, args=(Park_frame.copy(), control_signals))
            traffic_light_thread = threading.Thread(target=detect_traffic_light, args=(frame.copy(), control_signals))
            red_light_thread = threading.Thread(target=detect_red_light, args=(frame.copy(), control_signals))

            ox_thread.start()
            xo_thread.start()
            traffic_light_thread.start()
            red_light_thread.start()

        except Exception as E:
            print('- ERROR',E)


        # Wait for threads to finish
        ox_thread.join()
        xo_thread.join()        
        traffic_light_thread.join()
        red_light_thread.join()

        # IR Avoid sensor
        if LeftSensorValue == 0 or RightSensorValue == 0:
            p.start(20)
        elif LeftSensorValue == 1 and RightSensorValue == 1:
            p.stop()
        else :
            None

        print('traffic:',control_signals['traffic_light'],'red:',control_signals['red_light'])

        # Autonomous driving logic based on detections
        if signal != 0:
            car.Car_Stop()  
            time.sleep(0.1)
            if not control_signals['red_light']:
                if control_signals['traffic_light']:
                    signal = 0

            if signal == 1:
                rotate_servo(1, 104)    
                rotate_servo(2, 115)
            else:
                rotate_servo(1, 99)
                rotate_servo(2, 130)
        else:
            if control_signals['ox']:
                print("Sign 'OX' detected! Parking...")
                ox()
                val = 1
            # if control_signals['xo']:
            #     print("Sign 'XO' detected! Parking...")
            #     xo()
            #     val = 1
            #     time.sleep(0.5)
            elif control_signals['red_light']:
                signal = 1
                print("Red light detected! Stopping...")
                car.Car_Stop()
                time.sleep(0.1)
            else:
                processed_frame = process_frame(frame)
                histogram = np.sum(processed_frame, axis=0)
                direction = decide_direction(histogram)
                control_car(direction)
                cv2.imshow('threshold', processed_frame)


        cv2.imshow('Frame', frame)

        if val == 1:
            break

        # Pause/Unpause and Exit logic
        key = cv2.waitKey(1) & 0xFF
        if key == 32:  # Space bar to pause/unpause
            cv2.waitKey(0)  # Wait until any key is pressed
        elif key == 27:  # ESC to quit
            car.Car_Stop()
            break

except Exception as e:
    print(f"Error occurred: {e}")

finally:
    print('- THE END -')
    p.stop()
    car.Car_Stop()
    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()