import queue
import threading
import requests
from logger import logger

from config import INSTANCE_ID, PROVIDERS

event_queue = queue.Queue()

session = requests.Session()


def send(provider, event):

    payload = {
        "instance": INSTANCE_ID,
        "status": event.status,
        "public_url": event.public_url,
        "provider": "ngrok",
    }

    for url in provider["urls"]:
        url = url.strip()

        if not url:
            continue

        logger.info("[%s] Enviando atualização para %s", provider["name"], url)

        logger.debug("[%s] Payload: %s", provider["name"], payload)

        try:

            response = session.post(
                url,
                json=payload,
                timeout=10,
            )

            logger.info("[%s] Resposta de %s: HTTP %s", provider["name"], url, response.status_code)

            logger.debug("[%s] Corpo da resposta: %s", provider["name"], response.text)

            response.raise_for_status()

            logger.info("[%s] Atualização enviada com sucesso para %s", provider["name"], url)

        except requests.RequestException as exc:

            status = (
                exc.response.status_code
                if exc.response is not None
                else "SEM_RESPOSTA"
            )

            body = (
                exc.response.text
                if exc.response is not None
                else ""
            )

            logger.exception("[%s] Falha ao enviar para %s | HTTP=%s | Resposta=%s", provider["name"], url, status, body)

def worker():

    while True:

        event = event_queue.get()

        for provider in PROVIDERS:

            try:
               
                send(provider, event)

                print(
                    f"[{provider['name']}] OK"
                )

            except Exception as e:

                print(
                    f"[{provider['name']}] {e}"
                )

        event_queue.task_done()


def start():

    t = threading.Thread(
        target=worker,
        daemon=True,
    )

    t.start()