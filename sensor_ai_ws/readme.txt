터미널에서 gedit ~/.bashrc 를 열어서 강사의 가이드에 따라 편집하고 저장합니다.
모든 터미널을 끄고 새로운 터미널을 열어서 예제를 진행합니다.


# 1. 카메라 예제

roslaunch ros_sensor_test camera_test.launch


# 2. 라이다 예제

# 2.1 ROS 라이다 기본 예제
파란색 라이다

roslaunch ydlidar lidar_view.launch

검은색 라이다

roslaunch camsense_driver view.launch


# 2.2 ROS 라이다 응용 예제
파란색 라이다

roslaunch ros_sensor_test lidar_sub_test.launch

검은색 라이다

roslaunch ros_sensor_test lidar_sub_testC.launch

손을 가까이 대서 근접 거리 경고 확인

Ctl-C
