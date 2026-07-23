import requests
import time

from notifier import event_queue
from models import TunnelEvent
from config import (
    NGROK_API,
    CHECK_INTERVAL,
    FAILURES_TO_OFFLINE,
)

session = requests.Session()


class Monitor:

    def __init__(self):

        self.state = "UNKNOWN"
        self.url = None
        self.failures = 0

    def emit(self, status, url):

        event_queue.put(
            TunnelEvent(
                status=status,
                public_url=url,
            )
        )

    def online(self, url):

        self.failures = 0

        changed = (
            self.state != "ONLINE"
            or self.url != url
        )

        if changed:

            print("ONLINE")

            self.emit("online", url)

        self.state = "ONLINE"
        self.url = url

    def offline(self):

        if self.state != "OFFLINE":

            print("OFFLINE")

            self.emit("offline", None)

        self.state = "OFFLINE"
        self.url = None

    def get_url(self):

        r = session.get(
            NGROK_API,
            timeout=5,
        )

        r.raise_for_status()

        tunnels = r.json()["tunnels"]

        if not tunnels:

            return None

        return tunnels[0]["public_url"]

    def run(self):

        while True:

            try:

                url = self.get_url()

                if url:

                    self.online(url)

                else:

                    self.failures += 1

            except Exception:

                self.failures += 1

            if self.failures >= FAILURES_TO_OFFLINE:

                self.offline()

            time.sleep(CHECK_INTERVAL)