import cv2
import numpy as np
import RPi.GPIO as GPIO
import YB_Pcb_Car
import threading
import time
import random

cnt = 0

# Camera and car initialization
cap = cv2.VideoCapture(0)
cap.set(3, 320)  # Set width
cap.set(4, 240)  # Set height
cap.set(cv2.CAP_PROP_BRIGHTNESS, 37)
cap.set(cv2.CAP_PROP_CONTRAST, 37)
cap.set(cv2.CAP_PROP_SATURATION, 20)
cap.set(cv2.CAP_PROP_GAIN, 20)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
cap.set(cv2.CAP_PROP_EXPOSURE , 500)

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
MOTOR_UP_SPEED = 55    #  / 55
MOTOR_DOWN_SPEED = 40   # / 40
DETECT_VALUE = 63        # 55 / 밝은거 = 70 =======================================================================================================================

# Parking lot color detection
# lower_yellow = (18, 110, 120) 
# upper_yellow = (19+5, 255, 255)
# lower_yellow = (30, 93, 100) 
# upper_yellow = (41, 240, 180)

# Haar Cascade models
ox_cascade = cv2.CascadeClassifier('cascadeJoOX.xml')    # OX
xo_cascade = cv2.CascadeClassifier('cascadeJoXO.xml')    # XO  cascade_xo2.xml for A track
traffic_light_cascade = cv2.CascadeClassifier('cascadeJOG.xml') # Traffic LIght baisically Green light
red_light_cadcade = cv2.CascadeClassifier('cascade_red_3.xml')    # RED Light
obstacle_cadcade = cv2.CascadeClassifier('cascade_obsta.xml')    # RED Light

# Detection functions
def detect_ox(frame, control_signals):
    # gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    ox = ox_cascade.detectMultiScale(frame, scaleFactor=1.13, minNeighbors=1)
    # ox = ox_cascade.detectMultiScale(frame)
    if not len(ox) : 
        return
    for (x, y, w, h) in ox:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
    control_signals['ox'] = len(ox) > 0

def detect_xo(frame, control_signals):
    # gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    xo = xo_cascade.detectMultiScale(frame, scaleFactor=1.31, minNeighbors=3)  # was 1.12 3
    # xo = xo_cascade.detectMultiScale(frame)
    if not len(xo) : 
        return
    for (x, y, w, h) in xo:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
    control_signals['xo'] = len(xo) > 0

def detect_traffic_light(frame, control_signals):
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    traffic_lights = traffic_light_cascade.detectMultiScale(frame, scaleFactor=1.12, minNeighbors=1) # was 1.12 1
    # traffic_lights = traffic_light_cascade.detectMultiScale(gray)
    if not len(traffic_lights) : 
        return
    for (x, y, w, h) in traffic_lights:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
    control_signals['traffic_light'] = len(traffic_lights) > 0

def detect_red_light(frame, control_signals):
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    red_lights = red_light_cadcade.detectMultiScale(frame, scaleFactor=1.18, minNeighbors=2)
    # red_lights = red_light_cadcade.detectMultiScale(frame)
    if not len(red_lights) : 
        return
    for (x, y, w, h) in red_lights:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    control_signals['red_light'] = len(red_lights) > 0

def detect_obstacle(frame, control_signals):
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    obstacle = obstacle_cadcade.detectMultiScale(frame, scaleFactor=1.13, minNeighbors=1)
    # obstacle = obstacle_cadcade.detectMultiScale(gray)
    if not len(obstacle) : 
        return
    for (x, y, w, h) in obstacle:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    control_signals['obstacle'] = len(obstacle) > 0

# Autonomous driving functions 
def process_frame(frame, pts_src):
    pts_dst = np.float32([[0, 240], [320, 240], [320, 0], [0, 0]])
    pts = pts_src.reshape((-1, 1, 2)).astype(np.int32)
    frame = cv2.polylines(frame, [pts], isClosed=True, color=(0, 0, 255), thickness=None)

    # Stratch Road cut
    mat_affine = cv2.getPerspectiveTransform(pts_src, pts_dst)
    frame_transformed = cv2.warpPerspective(frame, mat_affine, (320, 240))
    # cv2.imshow('frame_startch', frame_transformed)

    gray_frame = cv2.cvtColor(frame_transformed, cv2.COLOR_RGB2GRAY)
    _, binary_frame = cv2.threshold(gray_frame, DETECT_VALUE, 255, cv2.THRESH_BINARY)
    cv2.imshow('threshold', binary_frame)
    return binary_frame

def parking_frame(frame):
    pts_park = np.float32([[0, 180], [320, 180], [320, 115], [0, 115]])
    pts_dst = np.float32([[0, 240], [320, 240], [320, 0], [0, 0]])
    pts = pts_park.reshape((-1, 1, 2)).astype(np.int32)
    # frame = cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 255), thickness=1)

    # Stratch Parking lot cut
    mat_affine_2 = cv2.getPerspectiveTransform(pts_park, pts_dst)
    frame_transformed_2 = cv2.warpPerspective(frame, mat_affine_2, (320, 240))
    # cv2.imshow('frame_startch2', frame_transformed_2)
    return frame_transformed_2

def decide_direction(histogram):
    left = int(np.sum(histogram[:int(len(histogram) / 4)]))
    right = int(np.sum(histogram[int(3 * len(histogram) / 4):]))
    up = np.sum(histogram[int(len(histogram) / 4):int(3 * len(histogram) / 4)])

    print("Left:", left, end=' ')
    print("Right:", right, end=' ')
    print("Neutral:", up)

    # if right + left > 4000000:
    #     return "LINE"
    if abs(right - left) > 200000:
        return "LEFT" if right > left else "RIGHT"
    elif up < 100000:
        return "UP"
    else:
        return "UP"

def control_car(direction):
    print(f"Controlling car: {direction}")  # new -13 > -15 > 13
    if direction == "UP":
        rotate_servo(1, 99)
        car.Car_Run(MOTOR_UP_SPEED -5 , MOTOR_UP_SPEED -5)
    elif direction == "LEFT":
        rotate_servo(1, 112)
        car.Car_Left(MOTOR_DOWN_SPEED, MOTOR_UP_SPEED)
    elif direction == "RIGHT":
        rotate_servo(1, 86)
        car.Car_Right(MOTOR_UP_SPEED, MOTOR_DOWN_SPEED)
    elif direction == "LINE":
        rotate_servo(1, 99)
        car.Car_Right(MOTOR_DOWN_SPEED -5, MOTOR_DOWN_SPEED -5)
        # time.sleep(0.2)

# Parking system
def ox():
    MOTOR_UP_SPEED = 45    # Speed range: 65 ~ 125 / 50
    MOTOR_DOWN_SPEED = 35   # 25- 30 / 35
    print(' - OX - ')
    car.Car_Left(MOTOR_DOWN_SPEED, MOTOR_UP_SPEED)
    time.sleep(1)
    car.Car_Run(MOTOR_UP_SPEED - 10, MOTOR_UP_SPEED - 10)
    time.sleep(1.2)
    car.Car_Right(MOTOR_UP_SPEED, MOTOR_DOWN_SPEED)
    time.sleep(1.3)
    car.Car_Run(MOTOR_UP_SPEED - 10, MOTOR_UP_SPEED - 10)
    time.sleep(1)
    car.Car_Stop
    # time.sleep(1)

def xo():
    print(' - XO - ')
    MOTOR_UP_SPEED = 45    # Speed range: 65 ~ 125 / 50
    MOTOR_DOWN_SPEED = 35   # 25- 30 / 35
    car.Car_Right(MOTOR_UP_SPEED, MOTOR_DOWN_SPEED)
    time.sleep(1.4)
    car.Car_Run(MOTOR_UP_SPEED - 10, MOTOR_UP_SPEED - 10)
    time.sleep(1.6)
    car.Car_Left(MOTOR_DOWN_SPEED, MOTOR_UP_SPEED)
    time.sleep(1.1)
    car.Car_Run(MOTOR_UP_SPEED - 10, MOTOR_UP_SPEED - 10)
    time.sleep(1)
    car.Car_Stop
    # time.sleep(1)

# camera servo
def rotate_servo(servo_id, angle):
    car.Ctrl_Servo(servo_id, angle)

# Main loop
try:
    rotate_servo(1, 100)  # Rotate servo at S1 to 90 degrees 좌우 99
    rotate_servo(2, 117)  #117 <> 13

    val = 0
    signal = 0
    count = 0
    count_old = 0
    str = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame from camera.")
            break

        # Frame for Parking lot
        Park_frame = parking_frame(frame)
        # Park_color = cv2.cvtColor(Park_frame, cv2.COLOR_RGB2HSV)       
        # mask_hsv_yellow,_,_ = cv2.split(Park_color)
        # mask_hsv_yellow = cv2.inRange(Park_color, lower_yellow, upper_yellow) 
        # # mask_hsv_yellow = cv2.inRange(Park_color,(0, 100, 100), (10, 255, 255) )
        # mean_of_hue = cv2.mean(mask_hsv_yellow)[0]
        # print('Color recog :', mean_of_hue)

        # Shared control signals dictionary
        control_signals = {'ox': False, 'xo': False, 'traffic_light': False, 'red_light': False, 'obstacle': False}

        # Create and start threads for detection tasks
        try:
            ox_thread = threading.Thread(target=detect_ox, args=(Park_frame.copy(), control_signals)) # OX
            xo_thread = threading.Thread(target=detect_xo, args=(Park_frame.copy(), control_signals)) # XO
            traffic_light_thread = threading.Thread(target=detect_traffic_light, args=(frame.copy(), control_signals))
            red_light_thread = threading.Thread(target=detect_red_light, args=(frame.copy(), control_signals))
            obstacle_thread = threading.Thread(target=detect_obstacle, args=(frame.copy(), control_signals))

            ox_thread.start() # OX
            xo_thread.start() # XO
            traffic_light_thread.start()
            red_light_thread.start()
            obstacle_thread.start()

        except Exception as E:
            print('- ERROR',E)


        # Wait for threads to finish
        ox_thread.join() # OX
        xo_thread.join() # XO  
        traffic_light_thread.join()
        red_light_thread.join()
        obstacle_thread.join()

        # Range Detector
        LeftSensorValue  = GPIO.input(AvoidSensorLeft)
        RightSensorValue = GPIO.input(AvoidSensorRight)

        # IR Avoid sensor
        if LeftSensorValue == 0 or RightSensorValue == 0:
            # car.Car_Left(MOTOR_DOWN_SPEED, MOTOR_UP_SPEED+10)
            p.start(20)
        elif control_signals['obstacle']:
            rotate_servo(1, 112)
            car.Car_Left(MOTOR_DOWN_SPEED, MOTOR_UP_SPEED+35)     
            time.sleep(0.01)
            p.start(20)
        elif LeftSensorValue == 1 and RightSensorValue == 1:
            p.stop()
        else : None


        print('traffic:',control_signals['traffic_light'],'red:',control_signals['red_light'])

        # Autonomous driving logic based on detections
        if signal != 0 and str != 1:
            car.Car_Stop()  
            if not control_signals['red_light']:
                if control_signals['traffic_light']:
                    signal = 0

            if signal == 1:
                rotate_servo(1, 103)    
                rotate_servo(2, 115)
                if count < 32:
                    time.sleep(0.05)
                    rotate_servo(1, 95+count)
                    count_old = count
                    count += 1
                    print(count)
                else: count = 1
            else:
                time.sleep(0.2)
                rotate_servo(1, 99)
                rotate_servo(2, 131)
                str = 1
        else:
            # if control_signals['ox']:
            #     print("Sign 'OX' detected! Parking...") # OX ===================================================================================================
            #     ox()
            #     val = 1
            if control_signals['xo']:
                print("Sign 'XO' detected! Parking...") # XO
                xo()
                val = 1
            elif control_signals['red_light'] and str != 1:
                signal = 1
                count = 1
                print("Red light detected! Stopping...")
                car.Car_Stop()
                rotate_servo(1, 109)    
                rotate_servo(2, 115)
                time.sleep(0.05)
            elif str != 1:
                MOTOR_UP_SPEED = 40    # Speed range: 65 ~ 125 / 50
                MOTOR_DOWN_SPEED = 30   # 25- 30 / 35
                pts_src2 = np.float32([[20, 240], [250, 240], [250, 220], [20, 220]])
                processed_frame = process_frame(frame,pts_src2)
                histogram = np.sum(processed_frame, axis=0)
                direction = decide_direction(histogram)
                control_car(direction)
            else:
                MOTOR_UP_SPEED = 51    # Speed range: 65 ~ 125 / 50
                MOTOR_DOWN_SPEED = 42   # 25- 30 / 35
                # pts_src = np.float32([[5, 240], [305, 240], [305, 180], [5, 180]]) # 
                pts_src = np.float32([[5, 240], [315, 240], [315, 180], [5, 180]]) # 중립 
                processed_frame = process_frame(frame,pts_src)
                histogram = np.sum(processed_frame, axis=0)
                direction = decide_direction(histogram)
                control_car(direction)
                    


        cv2.imshow('Frame', frame)

        if val == 1:
            break

        # Pause/Unpause and Exit logic
        key = cv2.waitKey(1) & 0xFF
        if key == 32:  # Space bar to pause/unpause
            cv2.waitKey(0)  # Wait until any key is pressed
        elif key == 27:  # ESC to quit
            p.stop()
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