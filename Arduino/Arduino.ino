#include <Servo.h>

// 두 개의 서보모터 객체 생성
Servo servoX; // 좌우 서보모터 (9번 핀)
Servo servoY; // 상하 서보모터 (10번 핀)

int posX = 90; // 서보 X의 초기 위치 (중간)
int posY = 90; // 서보 Y의 초기 위치 (중간)

void setup() {
  Serial.begin(9600); // 시리얼 통신 시작

  // 서보모터 핀 할당
  servoX.attach(9);
  servoY.attach(10);

  // 서보모터 초기 위치로 이동
  servoX.write(posX);
  servoY.write(posY);
}

void loop() {
  if (Serial.available() > 0) {
    String receivedData = Serial.readStringUntil('\n'); // 시리얼 데이터 수신

    if (receivedData.startsWith("left")) {
      posX = constrain(posX - 10, 0, 180); // 왼쪽으로 10도 이동
      servoX.write(posX);
    } else if (receivedData.startsWith("right")) {
      posX = constrain(posX + 10, 0, 180); // 오른쪽으로 10도 이동
      servoX.write(posX);
    } else if (receivedData.startsWith("up")) {
      posY = constrain(posY - 10, 0, 180); // 위로 10도 이동
      servoY.write(posY);
    } else if (receivedData.startsWith("down")) {
      posY = constrain(posY + 10, 0, 180); // 아래로 10도 이동
      servoY.write(posY);
    }

    // 서보 위치 상태를 시리얼로 피드백
    Serial.print("X: ");
    Serial.print(posX);
    Serial.print(", Y: ");
    Serial.println(posY);
  }
}
