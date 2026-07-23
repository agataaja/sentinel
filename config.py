import os

NGROK_API = os.getenv(
    "NGROK_API",
    "http://ngrok:4040/api/tunnels"
)

CHECK_INTERVAL = 5
FAILURES_TO_OFFLINE = 3

INSTANCE_ID = os.getenv("INSTANCE_ID")

PROVIDERS = [
    {
        "name": "Arena",
        "urls": os.getenv("REGISTER_URL", "").split(","),
    },

    # amanhã...
    # {
    #     "name": "Dashboard",
    #     "url": ...
    # }
]