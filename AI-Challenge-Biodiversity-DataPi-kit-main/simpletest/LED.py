# import
from machine import Pin
import utime

# def 함수: LED 제어 함수 정의
def led_on(led_pin):
    led_pin.value(1)

def led_off(led_pin):
    led_pin.value(0)

def led_toggle(led_pin):
    led_pin.value(not led_pin.value())

# GPIO 핀 설정
led_pin = Pin(28, Pin.OUT)  # 예시로 빨간색 LED사용

# while True 루프: LED 제어 예시
while True:
    led_on(led_pin)     # LED 켜기
    utime.sleep(1)
    led_off(led_pin)    # LED 끄기
    utime.sleep(1)