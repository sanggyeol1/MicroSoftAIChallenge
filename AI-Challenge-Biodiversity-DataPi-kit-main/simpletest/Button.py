from machine import Pin
from utime import sleep
import utime 

# GPIO 22번 핀에 연결된 LED를 출력 모드로 설정합니다.
Yled = Pin(22, Pin.OUT)

# GPIO 13번 핀에 연결된 버튼을 입력 모드로 설정합니다. 내부 풀업 저항을 활성화합니다.
Rbutton = Pin(13, Pin.IN, Pin.PULL_UP)

# GPIO 28번 핀에 연결된 또 다른 LED를 출력 모드로 설정합니다.
Rled = Pin(28, Pin.OUT)

# GPIO 2번 핀에 연결된 또 다른 버튼을 입력 모드로 설정합니다. 이 역시 내부 풀업 저항을 활성화합니다.
Lbutton = Pin(2, Pin.IN, Pin.PULL_UP)

# 무한 루프를 통해 버튼의 상태를 지속적으로 확인하고 LED를 제어합니다.
while True:
    # Lbutton의 상태를 출력합니다. (눌렸을 때 0, 눌리지 않았을 때 1)
    print(Lbutton.value())

    # Lbutton이 눌렸을 경우 Rled를 켭니다.
    if Lbutton.value() == 0:
        Rled.value(True)
    else:
        # Lbutton이 눌리지 않았을 경우 Rled를 끕니다.
        Rled.value(False)

    # Rbutton의 상태를 출력합니다.
    print(Rbutton.value())

    # Rbutton이 눌렸을 경우 Yled를 켭니다.
    if Rbutton.value() == 0:
        Yled.value(True)
    else:
        # Rbutton이 눌리지 않았을 경우 Yled를 끕니다.
        Yled.value(False)

    # 0.1초마다 반복합니다.
    utime.sleep(0.1)



