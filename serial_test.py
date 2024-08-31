import serial
import time

# 시리얼 포트와 통신 속도를 설정합니다.
# 'COM3'는 윈도우에서의 시리얼 포트 예시이며, 다른 운영체제에서는 '/dev/ttyUSB0' 또는 '/dev/ttyACM0'와 같은 포트를 사용합니다.
# Arduino IDE의 시리얼 모니터에서 확인한 포트와 동일하게 설정해야 합니다.
ser = serial.Serial('COM4', 9600)  # 포트 이름과 Baudrate 설정
time.sleep(2)  # 시리얼 연결이 안정될 때까지 대기

# Arduino에 데이터를 전송하는 함수
def send_data(data):
    ser.write(data.encode())  # 문자열을 바이트로 변환하여 송신
    print(f"Sent: {data}")

# 예시: "Hello, Arduino!" 문자열을 Arduino로 송신
send_data("Hello, Arduino!")

# 시리얼 포트 닫기
ser.close()
