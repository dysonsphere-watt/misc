from datetime import datetime, timezone
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from dotenv import load_dotenv
import random
import json
import time
import os

VID = os.getenv("ROBOT_VID", "ds0001")
BROKER = os.getenv("MQTT_HOST", "watt-emqx5.blackstone-aa019cfd.southeastasia.azurecontainerapps.io")
PORT = int(os.getenv("MQTT_PORT", 1883))
TOPIC = f"/up/{VID}"
USERNAME = os.environ.get("MQTT_USERNAME", "watt-evc-robot")
PASSWORD = os.environ.get("MQTT_PASSWORD", "qCjEgR0mHxO4Jt1W")

c_temp, b_temp, btr_temps = 20.0, 30.0, [30.0, 30.0]

t0 = time.time()


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")


def on_message(client, userdata, msg: mqtt.MQTTMessage):
    print(f"Received message from {TOPIC}")


def gen_int(min_val: int, max_val: int) -> int:
    return random.randint(min_val, max_val)


def gen_float(min_val: float, max_val: float) -> float:
    return random.uniform(min_val, max_val)


def inc_temp(delta: float, limit: float):
    global c_temp, b_temp, btr_temps

    c_temp += delta
    b_temp += delta
    for i in range(len(btr_temps)):
        btr_temps[i] += delta

    if c_temp > limit:
        c_temp = limit
    if b_temp > limit:
        b_temp = limit
    for i in range(len(btr_temps)):
        if btr_temps[i] > limit:
            btr_temps[i] = limit


def gen_msg() -> dict:
    mem = gen_int(0, 128)
    sto = gen_int(0, 128)

    return {
        "ver": os.environ.get("ROBOT_PROTOCOL_VER", "0.18"),
        "vid": VID,
        "seq": 1,
        "ack": 1,
        "type": 51,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "data": {
            "ret_code": 0,
            "mode_val": 1,
            "dev_type": "robot",
            "task_id": 0,
            "task_plan": "No Task",
            "task_status": 0,
            "car_status": {
                "c_sta_code": "waiting",
                "pos_id": "P0",
                "sub_pos_id": "1",
                "t_pos_id": "P0",
                "sub_t_pos_id": "1",
                "c_btr": gen_int(50, 100),
            },
            "btr_status": {
                "b_sta_code": "btr_charging",
                "b_btr": gen_int(50, 100),
                "chg_gun": 1,
                "chg_line": 1,
                "remain_chg_time": gen_int(0, 1800)
            },
            "detail": {
                "car_detail": {
                    "c_temp": int(c_temp),
                    "c_humidity": gen_int(0, 100),
                    "c_xyz": "0,0,0",
                    "c_pos": "0,0",
                    "c_speed": f"{gen_int(1, 8)}km/h"
                },
                "btr_detail": {
                    "b_temp": int(b_temp),
                    "b_battery": gen_int(50, 100),
                    "b_out_current": gen_int(19, 20),
                    "b_out_voltage": gen_int(219, 220),
                    "b_in_current": gen_int(19, 20),
                    "b_in_voltage": gen_int(219, 220),
                },
                "robot_info": {
                    "pose": {
                        "local_x": gen_float(0, 100),
                        "local_y": gen_float(0, 100),
                        "angle": gen_float(0, 90),
                    },
                    "is_charging": False,
                    "battery": gen_float(50, 100),
                    "battery_tempature": btr_temps,
                    "speed": gen_float(1, 8),
                    "is_obstacle_brake": False,
                    "running_time": round(time.time() - t0, 2),
                    "system_info": {
                        "cpu_info": {
                            "cpu0": {
                                "usage": gen_float(0, 1)
                            },
                            "cpu1": {
                                "usage": gen_float(0, 1)
                            },
                        },
                        "memory_info": {
                            "total": 128,
                            "used": mem,
                            "usage": round(mem/128, 2),
                        },
                        "storage_info": {
                            "total": 128,
                            "used": sto,
                            "usage": round(sto/128, 2),
                        }
                    },
                    "sensor_info": {
                        "lidar_status": 0,
                        "imu_status": 0,
                        "laser_1_status": 0,
                        "laser_2_status": 0,
                        "can_status": 0
                    }
                }
            },
            "ad_left": 1,
            "ad_right": 1,
            "door_left": 1,
            "door_right": 1
        },
    }


if __name__ == "__main__":
    load_dotenv()

    client_id = VID
    client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2, client_id=client_id)
    client.on_connect = on_connect
    client.username_pw_set(USERNAME, PASSWORD)
    client.connect(BROKER, PORT)
    client.loop_start()

    f = open("playback.txt", "r")
    content = f.read()
    f.close()

    messages = content.split("\n\n")
    messages = [msg.strip() for msg in messages]

    i = 0
    while True:
        msg = messages[i]
        print(msg)
        client.publish(TOPIC, msg)

        # Cycle back if necessary
        i += 1
        if i >= len(messages):
            i = 0

        time.sleep(1)

    client.loop_stop()
    client.disconnect()
