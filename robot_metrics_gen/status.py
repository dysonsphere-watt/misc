from datetime import datetime, timezone
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from dotenv import load_dotenv
import random
import json
import time
import os

VID = os.environ.get("ROBOT_VID")
BROKER = os.environ.get("MQTT_HOST", "")
PORT = int(os.environ.get("MQTT_PORT", 0))
TOPIC = f"/up/{VID}"
USERNAME = os.environ.get("MQTT_USERNAME")
PASSWORD = os.environ.get("MQTT_PASSWORD")

t0 = time.time()


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")


def on_message(client, userdata, msg: mqtt.MQTTMessage):
    print(f"Received message from {TOPIC}")


def gen_int(min_val: int, max_val: int) -> int:
    return random.randint(min_val, max_val)


def gen_float(min_val: float, max_val: float) -> float:
    return round(random.uniform(min_val, max_val), 2)


def gen_msg() -> dict:
    mem = gen_int(0, 128)
    sto = gen_int(0, 128)

    return {
        "id": "",
        "ver": "0.13",
        "vid": "ds0002",
        "seq": 0,
        "ack": 0,
        "type": 1,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "data": {
            "dev_type": "EVC",
            "status_type": "detail"
        }
    }


if __name__ == "__main__":
    load_dotenv()

    client_id = f"robot_metrics_retrieval_{gen_int(1000, 9999)}"
    client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2, client_id=client_id)
    client.on_connect = on_connect
    client.username_pw_set(USERNAME, PASSWORD)

    client.will_set("lwt_test", f"you are receiving this because client {client_id} unexpectedly disconnected")

    client.connect(BROKER, PORT)
    client.loop_start()

    client.subscribe(TOPIC)
    client.on_message = on_message

    while True:
        msg = gen_msg()
        # client.publish(TOPIC, json.dumps(msg))
        time.sleep(10)

    client.loop_stop()
    client.disconnect()
