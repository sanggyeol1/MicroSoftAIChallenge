import time
import machine
import onewire, ds18x20

# GPIO 1번 핀에 OneWire 버스를 생성합니다.
data = machine.Pin(1)
temp_wire = onewire.OneWire(data) # GPIO 1번 핀에서 OneWire 버스 생성

# OneWire 버스를 사용하여 DS18X20 온도 센서 객체를 생성합니다.
temp_sensor = ds18x20.DS18X20(temp_wire)

# 버스에서 연결된 장치(온도 센서)를 스캔합니다.
roms = temp_sensor.scan()
print(len(roms), 'temperature sensor found')  # 연결된 온도 센서의 수를 출력합니다.

# 무한 루프를 통해 온도를 지속적으로 읽습니다.
while True:
    print('temperatures:', end=' ')
    # 모든 연결된 온도 센서로부터 온도를 읽기 시작합니다.
    temp_sensor.convert_temp()
    time.sleep_ms(100)  # 온도 변환에 필요한 시간을 기다립니다.

    # 각 온도 센서의 ROM 주소에 대해 온도를 읽고 출력합니다.
    for rom in roms:
        t = temp_sensor.read_temp(rom)
        print('{:6.2f}'.format(t), end=' ')  # 읽은 온도를 포맷하여 출력합니다.
    print()  # 줄바꿈을 출력하여 온도 출력을 구분합니다.
