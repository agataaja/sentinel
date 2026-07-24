import queue
import threading
import requests
from logger import logger

from config import INSTANCE_ID, PROVIDERS, NOTIFY_RETRY_DELAY_SECONDS

event_queue = queue.Queue()

session = requests.Session()


def _post(url, payload):

    response = session.post(
        url,
        json=payload,
        timeout=10,
    )

    logger.info("Resposta de %s: HTTP %s", url, response.status_code)
    logger.debug("Corpo da resposta: %s", response.text)

    response.raise_for_status()


def _retry_once_later(provider_name, url, payload):

    def _retry():

        try:

            logger.info("[%s] Tentando reenvio para %s", provider_name, url)

            _post(url, payload)

            logger.info("[%s] Reenvio concluído com sucesso para %s", provider_name, url)

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

            logger.exception("[%s] Reenvio falhou para %s | HTTP=%s | Resposta=%s", provider_name, url, status, body)

    timer = threading.Timer(NOTIFY_RETRY_DELAY_SECONDS, _retry)
    timer.daemon = True
    timer.start()


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

            _post(url, payload)

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

            if exc.response is None:

                logger.warning(
                    "[%s] Endpoint indisponível sem resposta. Reenvio agendado em %ss para %s",
                    provider["name"],
                    NOTIFY_RETRY_DELAY_SECONDS,
                    url,
                )

                _retry_once_later(provider["name"], url, payload)

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