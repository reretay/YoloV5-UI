from pymavlink import mavutil

# 드론에 연결
the_connection = mavutil.mavlink_connection('0.0.0.0:14880')

# 명령을 보내기 전에 하트비트를 대기
the_connection.wait_heartbeat()

# GPS_RAW_INT 메시지를 1Hz로 요청
the_connection.mav.command_long_send(
    the_connection.target_system,
    the_connection.target_component,
    mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
    0,
    mavutil.mavlink.MAVLINK_MSG_ID_GPS_RAW_INT,
    1e6,  # 주파수 (마이크로초 단위, 여기서는 1 Hz)
    0, 0, 0, 0, 0
)


# GPS_RAW_INT 메시지를 수신 시도
msg = the_connection.recv_match(type='GPS_RAW_INT', blocking=True, timeout=1)
if msg:
    print(f"고도: {msg.alt / 1000.0} 미터")
    print(f"lat: {msg.lat}, lon: {msg.lon}")
else:
    print(f"Can't Get the GPS info")
