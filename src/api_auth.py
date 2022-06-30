from . import settings

import logging
import requests
import json

from .exceptions import BotException

logger = logging.getLogger(__name__)


class AuthAPI:
 
    def __init__(self):
        self.token = None


    def login(self, username, password):
        data = {
            "username": username,
            "password": password
        }
        try:
            response = requests.post(url=settings.APP_URL + "auth/token/login/", json=data)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                raise BotException(error=response.text, message=response.text)
            else:
                raise BotException(error=response.text, message="Ошибка авторизации, мы скоро её исправим.")

        result = json.loads(response.content)
        self.token = result.get("token")


    def login_anonymous(self):
        try:
            response = requests.post(url=settings.APP_URL + "auth/anonymous/login/")
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise BotException(error=response.text, message="Ошибка анонимного входа, мы скоро её исправим.")

        result = json.loads(response.content)
        self.token = result.get("token")

