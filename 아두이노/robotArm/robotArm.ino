#define inPin 3 //아두이노와 연결된 디지털 핀 3, high 시 로봇팔 동작 , 서로의 GND는 연결해야 함

void setup() {
  pinMode(inPin, INPUT);
  Serial.begin(57600);
  while (!Serial);  // 시리얼 포트가 열릴 때까지 대기

  // 로봇팔 초기화
  open_manipulator.setOpenManipulatorCustomJointId(11, 12, 13, 14, 15); // 기본 ID 설정
  open_manipulator.initOpenManipulator(true);
  Serial.println("OpenManipulator Init Complete");
}

void loop() {
  int state = digitalRead(inPin); // 핀의 상태를 읽음
  if(state == HIGH) { // 로봇팔 동작
    moveRobotArm();
  }
}

void moveRobotArm() {
  // 로봇팔을 임의의 6가지 위치로 순차적으로 이동시키는 예제
  double positions[6][5] = {
    {0.5, -0.5, 0.3, -0.3, 0.01},
    {0.4, -0.4, 0.2, -0.2, 0.02},
    {0.3, -0.3, 0.1, -0.1, 0.03},
    {0.2, -0.2, 0.0,  0.0,  0.04},
    {0.1, -0.1, -0.1, 0.1,  0.05},
    {0.0,  0.0, -0.2, 0.2,  0.06}
  };

  double time = 2.0; // 각 위치로 이동하는 시간 (초)

  for (int i = 0; i < 6; i++) {
    double j1 = positions[i][0];
    double j2 = positions[i][1];
    double j3 = positions[i][2];
    double j4 = positions[i][3];
    double gripper_pos = positions[i][4];

    // 로봇팔을 각 위치로 이동시키는 함수 호출
    moveJS(&open_manipulator, j1, j2, j3, j4, gripper_pos, time);

    // 다음 위치로 이동하기 전에 잠시 대기
    delay(time * 1000);
  }
}

// Move in Joint Space 
void moveJS(OpenManipulator *open_manipulator, double j1, double j2, double j3, double j4, double gripper_pos, double time) {
  static std::vector<double> target_angle;
  target_angle.clear();
  target_angle.push_back(j1);
  target_angle.push_back(j2);
  target_angle.push_back(j3);
  target_angle.push_back(j4);
  open_manipulator->makeJointTrajectory(target_angle, time); //로봇팔 조인트 목표 각도로 이동
  open_manipulator->makeToolTrajectory("gripper", gripper_pos); //그리퍼 이동
}
