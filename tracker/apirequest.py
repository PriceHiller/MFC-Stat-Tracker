import logging
import os
import sys

from urllib import parse

from aiohttp import ClientSession
from aiohttp import ClientConnectionError

log = logging.getLogger("__name__")


class APIError(Exception):

    def __init__(self, status_code: int, content):
        self.status_code = status_code
        self.content = content


class APIRequest:
    api_url = os.getenv("API_URL", default=None)
    if not api_url:
        log.critical(f"A(n) API URL (API_URL) was not passed to the environment")
        sys.exit(128)
    api_url = api_url.strip("/")
    log.debug(f"API url registered as {api_url}")
    api_token = os.getenv("API_TOKEN", default=None)
    if not api_token:
        log.critical(f"A(n) API Token (API_TOKEN) was not passed to the environment")
        sys.exit(128)
    headers = {"Authorization": "Bearer " + api_token}

    class Response:

        def __init__(self, json: dict, status: int):
            self.json = json
            self.status = status

    @staticmethod
    def verify_url(url: str, checks=("scheme", "netloc")):
        valid_url = parse.urlparse(url)
        return all([getattr(valid_url, check_attr) for check_attr in checks])

    @classmethod
    async def get(cls, endpoint: str = "/") -> Response:
        full_url = cls.api_url + endpoint
        if not cls.verify_url(full_url):
            return cls.Response({}, 418)
        async with ClientSession(headers=cls.headers) as session:
            try:
                log.debug(f"GET request issued to {full_url}")
                async with session.get(full_url, ssl=False) as get_session:
                    json_dict = await get_session.json() or {}
                    return cls.Response(json_dict, get_session.status)
            except ClientConnectionError as error:
                log.warning(f"Could not connect to the API at url {cls.api_url}, error: {error}")
                return cls.Response({}, 400)
            except UnicodeError:
                log.warning(f"Unicode error thrown due to URL, likely malformed, URL: {full_url}")
                return cls.Response({}, 400)

    @classmethod
    async def post(cls, endpoint: str = "/", data: dict = None) -> Response:
        full_url = cls.api_url + endpoint
        if not cls.verify_url(full_url):
            log.warning(f"URL {full_url} is not a valid url!")
            return cls.Response({}, 400)
        async with ClientSession(headers=cls.headers) as session:
            try:
                log.debug(f"POST request issued to {full_url}")
                async with session.post(full_url, json=data, ssl=False) as post_session:
                    json_dict = await post_session.json() or {}
                    return cls.Response(json_dict, post_session.status)
            except UnicodeError:
                log.warning(f"Unicode error thrown due to URL, likely malformed, URL: {full_url}")
                return cls.Response({}, 400)
            except ClientConnectionError as error:
                log.warning(f"Could not connect to the API at url {cls.api_url}, error: {error}")
                return cls.Response({}, 400)
