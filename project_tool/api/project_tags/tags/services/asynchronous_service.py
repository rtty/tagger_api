import logging
from datetime import datetime

from asgiref.sync import sync_to_async
from bus_api import BusApi
from django.conf import settings

# Get an instance of a logger
logger = logging.getLogger(__name__)


@sync_to_async
def asyn_update_project_tag(topic, originator, function):
    """
    Wrapper function
    :param topic: topic of the message
    :param originator: source of the message
    :param function: part of the view function that can be run asynchronously
    :return:
    """

    logging.info("Will run the update member asynchronously")
    run_asynchronously(topic, originator, function)


def run_asynchronously(topic, originator, function):
    """
    Runs function and publishes the results in the event bus
    :param topic: topic of the message
    :param originator: source of the message
    :param function: part of the view function that can be run asynchronously
    :return:
    """
    logging.info("Called run_asynchronously")
    client = BusApi(
        auth0_url=settings.CONFIG["auth0_url"],
        auth0_audience=settings.CONFIG["auth0_audience"],
        token_cache_time=settings.CONFIG["token_cache_time"],
        auth0_client_id=settings.CONFIG["auth0_client_id"],
        auth0_client_secret=settings.CONFIG["auth0_client_secret"],
        busapi_url=settings.CONFIG["busapi_url"],
        kafka_error_topic=settings.CONFIG["kafka_error_topic"],
        auth0_proxy_server_url=settings.CONFIG["auth0_proxy_server_url"],
    )

    time_stamp = datetime.utcnow().isoformat("T", "milliseconds") + "Z"
    response = function()

    payload = {
        "topic": topic,
        "payload": response,
        "originator": originator,
        "timestamp": time_stamp,
        "mime-type": "application/json",
    }

    logging.info("Sending payload %s", payload)
    client.post_event(payload)
