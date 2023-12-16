import network
import urequests
import ujson
from config import wifi_config, api_config

# Wi-Fi 설정
ssid = wifi_config['ssid']
password = wifi_config['password']

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

# Wi-Fi 연결 확인
while not station.isconnected():
    pass

print('Connection successful')
print(station.ifconfig())

# OpenWeatherMap API 설정
api_key = api_config['api_key']
city = 'Seoul'
url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'

# 날씨 데이터 요청 및 응답
response = urequests.get(url)
weather_data = response.json()
response.close()

# 필요한 데이터 추출
temperature = weather_data['main']['temp']
humidity = weather_data['main']['humidity']
weather_description = weather_data['weather'][0]['description']

# 출력
print(f'Temperature: {temperature}°C')
print(f'Humidity: {humidity}%')
print(f'Weather Description: {weather_description}')
