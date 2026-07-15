import os
import time
import signal
import sys

import requests

NGROK_API = os.getenv("NGROK_API", "http://ngrok:4040/api/tunnels")
REGISTER_URL = os.getenv("REGISTER_URL", "http://localhost:8001/api/arena/tunnel/register/")
INSTANCE_ID = os.getenv("INSTANCE_ID", "default-instance-id")
last_url = None


def notify(status, url=None):
    register_url = REGISTER_URL

    payload = {
        "instance": INSTANCE_ID,
        "status": status,
        "public_url": url,
        "provider": "ngrok",
    }

    headers = {}

    print(f"Sending notification to {register_url} with payload: {payload}")


    try:

        requests.post(
            register_url,
            json=payload,
            headers=headers,
            timeout=5
        )
        print(payload)
    except Exception as e:
        print(e)


def shutdown(*_):
    notify("offline")
    sys.exit(0)


signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

while True:
    try:
        r = requests.get(NGROK_API, timeout=3).json()

        tunnels = r.get("tunnels", [])

        if tunnels:
            url = tunnels[0]["public_url"]

            if url != last_url:
                notify("online", url)
                last_url = url

    except Exception as e:
        print(e)

    time.sleep(5)