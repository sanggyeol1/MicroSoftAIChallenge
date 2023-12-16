from machine import Pin
import utime

# LED와 버튼 핀 초기화
Yled = Pin(22, Pin.OUT)
Rled = Pin(28, Pin.OUT)
Rbutton = Pin(13, Pin.IN, Pin.PULL_UP)
Lbutton = Pin(2, Pin.IN, Pin.PULL_UP)

# 버튼 상태를 추적하는 변수 초기화
Rbutton_state = False
Lbutton_state = False

# 버튼이 눌렸을 때 호출될 핸들러 함수 정의
def Rbutton_handler(pin):
    global Rbutton_state
    # 버튼 상태 전환
    Rbutton_state = not Rbutton_state
    print("Rbutton_state:", end =' ')
    print(Rbutton_state)
    Yled.value(Rbutton_state)

def Lbutton_handler(pin):
    global Lbutton_state
    # 버튼 상태 전환
    Lbutton_state = not Lbutton_state
    print("Lbutton_state:", end =' ' )
    print(Lbutton_state)
    Rled.value(Lbutton_state)

# 버튼에 핸들러 등록
Rbutton.irq(trigger=Pin.IRQ_FALLING, handler=Rbutton_handler)
Lbutton.irq(trigger=Pin.IRQ_FALLING, handler=Lbutton_handler)

while True:
    utime.sleep(0.1)
