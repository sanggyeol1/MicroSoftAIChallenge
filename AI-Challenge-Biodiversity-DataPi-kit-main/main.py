import utime
from machine import Pin, I2C, PWM
from ds3231_port import DS3231
import onewire, ds18x20

# 글로벌 변수
sensing_active = False
recording_active = False
recording_interval = 1  # 데이터 기록 간격을 초 단위로 설정 (예: 1초마다 데이터 기록)
file = None # 파일 객체 초기화
button_pressed_time = 0 # 버튼 눌린 시간 기록 

# LED, 버튼, 부저 설정
YLed = Pin(22, Pin.OUT)
Rled = Pin(28, Pin.OUT)
Rbutton = Pin(13, Pin.IN, Pin.PULL_UP)
buzzer = PWM(Pin(15))

# I2C 설정
sdaPIN = Pin(8)
sclPIN = Pin(9)
i2c = I2C(0, sda=sdaPIN, scl=sclPIN)

# DS3231 RTC 및 DS18x20 온도 센서 설정
ds3231 = DS3231(i2c)
data = Pin(1)
temp_wire = onewire.OneWire(data)
temp_sensor = ds18x20.DS18X20(temp_wire)
roms = temp_sensor.scan()

# 버튼 핸들러 함수
def Rbutton_handler(pin):
    global sensing_active, recording_active, file, button_pressed_time

    current_time = utime.ticks_ms()
    if pin.value() == 0:  # 버튼이 눌렸을 때
        button_pressed_time = current_time
    else:  # 버튼이 떼어졌을 때
        if current_time - button_pressed_time > 1000:  # 버튼이 1초 이상 눌렸을 경우
            recording_active = not recording_active
            if recording_active:
                play_buzzer(2000)  # recording_active 시작 시 부저
                file = open('temperature_data.csv', 'a')  # 파일 열기
                # 파일에 새 데이터 세트가 추가될 때마다 구분자 삽입
                file.write("\n--- New Data ---\n")
                if file.tell() == len("---New Data ---\n"): #파일이 새로 생성되었다면 
                    file.write('Time,Temperature\n')
            else:
                if file:
                    file.close()  # 파일 닫기
                    file = None
                    play_buzzer(2000)   # recording_active 종료 시 부저
        else:  # 버튼이 1초 미만으로 눌렸을 경우
            sensing_active = not sensing_active
            play_buzzer(1000)  # sensing_active 시작 시 부저


# 부저를 울리는 함수
def play_buzzer(freq):
    buzzer.duty_u16(30000)
    buzzer.freq(freq)
    utime.sleep(0.1)
    buzzer.duty_u16(0)

# 버튼에 핸들러 등록
#Rbutton.irq(trigger=Pin.IRQ_FALLING, handler=Rbutton_handler)
Rbutton.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=Rbutton_handler)

# 메인 루프
while True:
    if sensing_active:
        YLed.value(1)  # YLed 켜기
        for rom in roms:
            temp_sensor.convert_temp()
            utime.sleep_ms(100)
            t = temp_sensor.read_temp(rom)
            print(t)
            YLed.value(0)  # YLed 끄기
            utime.sleep_ms(500)
    if recording_active:
        Rled.value(1)  # Rled 켜기
        # 데이터 기록 로직
        for rom in roms:
            temp_sensor.convert_temp()
            utime.sleep_ms(100)
            t = temp_sensor.read_temp(rom)
            dateTime = ds3231.get_time()
            timestamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(dateTime[0], dateTime[1], dateTime[2], dateTime[3], dateTime[4], dateTime[5])
            data_line = "{}, {:6.2f}\n".format(timestamp, t)
            print(t)
            if file:
                file.write(data_line)
            utime.sleep(recording_interval)  # 사용자가 설정한 기록 간격에 따라 대기
    else:
        Rled.value(0)  # Rled 끄기
    utime.sleep(0.1)
