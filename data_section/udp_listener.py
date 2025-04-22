import socket
import struct
import threading
from show_message import show_message


HEADER_FORMAT = "<HBBBBBQfII2B"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
UDP_IP = "0.0.0.0"
UDP_PORT = 5005

telemetry_data = []
lap_telemetry = {}
lap_times = {}

_listener_thread = None
_listener_running = False


def start_udp_listener():
    global _listener_thread, _listener_running
    if _listener_running:
        show_message("Az adatrögzítés már elindult!.")
        return
    _listener_running = True
    _listener_thread = threading.Thread(target=_listener_loop, daemon=True)
    _listener_thread.start()
    show_message(f"Adatok rögzítése elindult (UDP IP és port): {UDP_IP}:{UDP_PORT}")


def stop_udp_listener():
    global _listener_running
    _listener_running = False
    show_message("Adatrögzítés leállítva!")


def _listener_loop():
    global telemetry_data, lap_telemetry, lap_times, _listener_running
    current_lap_telemetry = []
    last_recorded_lap_num = -1
    current_lap_distance = 0.0
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    while _listener_running:
        try:
            data, _ = sock.recvfrom(2048)
            if len(data) < HEADER_SIZE:
                continue
            header = struct.unpack(HEADER_FORMAT, data[:HEADER_SIZE])
            packet_id = header[5]
            session_time = header[7]
            player_car_index = header[10]
            if session_time == 0:
                continue
            if packet_id == 6:
                telemetry_offset = HEADER_SIZE + (player_car_index * 60)
                fmt = "<HfffBBH"
                fmt_size = struct.calcsize(fmt)
                car_bytes = data[telemetry_offset: telemetry_offset + fmt_size]
                if len(car_bytes) < fmt_size:
                    continue
                speed, throttle, steer, brake, clutch, _, engine_rpm = struct.unpack(fmt, car_bytes)
                sample = (current_lap_distance, speed, engine_rpm, throttle, brake, steer)
                telemetry_data.append(sample)
                current_lap_telemetry.append(sample)
            elif packet_id == 2:
                lapdata_offset = HEADER_SIZE + (player_car_index * 57)
                lapdata_bytes = data[lapdata_offset: lapdata_offset + 57]
                if len(lapdata_bytes) < 57:
                    continue
                last_lap_time = struct.unpack_from("<I", lapdata_bytes, 0)[0]
                current_lap_num = struct.unpack_from("<B", lapdata_bytes, 33)[0]
                lap_distance = struct.unpack_from("<f", lapdata_bytes, 20)[0]
                current_lap_distance = lap_distance
                if last_lap_time > 0 and (current_lap_num - 1) > last_recorded_lap_num:
                    last_recorded_lap_num = current_lap_num - 1
                    lap_telemetry[last_recorded_lap_num] = current_lap_telemetry.copy()
                    lap_times[last_recorded_lap_num] = last_lap_time
                    current_lap_telemetry.clear()
        except Exception as e:
            show_message("Hiba az UDP adatok olvasása során:", e)

    sock.close()