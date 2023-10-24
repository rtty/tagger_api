import json
import logging

import requests

logging.basicConfig(level=logging.DEBUG)

# Get an instance of a logger
logger = logging.getLogger(__name__)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


class BusApi:
    """Provide communication with the API event bus"""

    def __init__(
        self,
        auth0_url,
        auth0_audience,
        token_cache_time,
        auth0_client_id,
        auth0_client_secret,
        busapi_url,
        kafka_error_topic,
        auth0_proxy_server_url,
    ):
        self.config = {
            "AUTH0_URL": auth0_url,
            "AUTH0_AUDIENCE": auth0_audience,
            "TOKEN_CACHE_TIME": token_cache_time,
            "AUTH0_CLIENT_ID": auth0_client_id,
            "AUTH0_CLIENT_SECRET": auth0_client_secret,
            "BUSAPI_URL": busapi_url,
            "KAFKA_ERROR_TOPIC": kafka_error_topic,
            "AUTH0_PROXY_SERVER_URL": auth0_proxy_server_url or auth0_url,
        }
        self.validate_inputs()

    def validate_inputs(self):
        """Validate inputs"""
        for key, val in self.config.items():
            if key == "TOKEN_CACHE_TIME":
                if not isinstance(val, int):
                    raise ValueError("{} has to be int value".format(key))
                if val <= 0:
                    raise ValueError("{} has to be positive value".format(key))
                continue
            if not isinstance(val, str):
                raise ValueError("{} has to be string".format(key))
            if key == "AUTH0_PROXY_SERVER_URL":
                continue
            if val == "":
                raise ValueError("{} cannot be empty string".format(key))

    def post_event(self, request_body):
        """
        Publish event to the API bus
        :param request_body: payload of the event message
        :return:
        """
        token = self.get_m2m_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(token),
        }
        response = requests.post(
            self.config["BUSAPI_URL"] + "/bus/events",
            headers=headers,
            data=json.dumps(request_body),
        )
        logging.info("response.status_code = %s", response.status_code)
        assert response.status_code == 204

    def get_m2m_token(self):
        """Get machine to machine token"""
        data = {
            "grant_type": "client_credentials",
            "client_id": self.config["AUTH0_CLIENT_ID"],
            "client_secret": self.config["AUTH0_CLIENT_SECRET"],
            "audience": self.config["AUTH0_AUDIENCE"],
            "auth0_url": self.config["AUTH0_URL"],
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            self.config["AUTH0_PROXY_SERVER_URL"],
            headers=headers,
            data=json.dumps(data),
        )
        assert response.status_code == 200
        response_as_json = json.loads(response.text)
        return response_as_json["access_token"]
