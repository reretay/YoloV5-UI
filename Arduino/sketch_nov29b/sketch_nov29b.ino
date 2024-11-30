#include <Servo.h>

// 두 개의 서보모터 객체 생성
Servo servoX; // 좌우 서보모터 (9번 핀)
Servo servoY; // 상하 서보모터 (10번 핀)

void setup() {
  Serial.begin(115200); // 시리얼 통신 시작

  // 서보모터 핀 할당
  servoX.attach(9);
  servoY.attach(10);

  // 초기 위치 설정 (중앙값)
  servoX.write(90); // 90도
  servoY.write(90); // 90도
}

void loop() {
  static String receivedData = ""; // 수신 데이터를 임시로 저장

  // 시리얼 데이터 수신
  while (Serial.available() > 0) {
    char receivedChar = Serial.read(); // 한 바이트씩 읽기

    if (receivedChar == '\n') {
      processReceivedData(receivedData);
      receivedData = ""; // 데이터를 처리한 후 초기화
    } else {
      receivedData += receivedChar; // 수신 데이터를 문자열로 조합
    }
  }
}

void processReceivedData(String data) {
  // 데이터 포맷: "diff_x,diff_y\n"
  int separatorIndex = data.indexOf(','); // 콤마 위치 찾기
  if (separatorIndex == -1) return; // 유효하지 않은 데이터 무시

  // 문자열 분리
  String diffXString = data.substring(0, separatorIndex);
  String diffYString = data.substring(separatorIndex + 1);

  // 문자열을 정수로 변환
  int diff_x = diffXString.toInt();
  int diff_y = diffYString.toInt();

  // -255 ~ 255를 0 ~ 180으로 매핑
  int angleX = map(diff_x, -255, 255, 0, 180);
  int angleY = map(diff_y, -255, 255, 0, 180);

  // 서보 모터에 각도 적용
  servoX.write(angleX);
  servoY.write(angleY);
}
