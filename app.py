import signal
import sys

from monitor import Monitor
from notifier import start, event_queue
from models import TunnelEvent


def shutdown(*_):

    event_queue.put(
        TunnelEvent(
            status="offline",
            public_url=None,
        )
    )

    event_queue.join()

    sys.exit(0)


signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

start()

Monitor().run()