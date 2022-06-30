from . import settings

import logging
import requests
import json

from .exceptions import BotException

logger = logging.getLogger(__name__)


class QuizAPI:

    def __init__(self, token):
        self.headers = {"Authorization": "token {0}".format(token)}
        self.bizfuncs = []
        self.bizfunc_choice = None
        self.questions = []
        self.question_choice = None
        self.options = []
        self.option_choice = None


    def fetch_bizfuncs(self):
        try:
            response = requests.get(url=settings.APP_URL + "api/supplier/bizfunc/", headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise BotException(error=response.text, message="Ошибка при получении бизнес-функций, мы скоро её исправим.")
        self.bizfuncs = json.loads(response.content)
        if len(self.bizfuncs) < 1:
            raise BotException(error="len(self.bizfuncs) < 1", message="Ошибка при получении списка бизнес-функций, мы скоро её исправим.")


    def fetch_questions(self):
        query_string = "?bizfunc_slug={0}".format(self.bizfuncs[self.bizfunc_choice].get("slug"))
        try:
            response = requests.get(url=settings.APP_URL + "api/audit/question/" + query_string, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise BotException(error=response.text, message="Ошибка при получении бизнес-функций, мы скоро её исправим.")
        self.questions = json.loads(response.content)
        if len(self.questions) < 1:
            raise BotException(error="len(self.questions) < 1", message="Ошибка при получении списка вопросов, мы скоро её исправим.")


    def fetch_options(self):
        query_string = "?question_slug={0}".format(self.questions[self.question_choice].get("slug"))
        try:
            response = requests.get(url=settings.APP_URL + "api/audit/option/" + query_string, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise BotException(error=response.text, message="Ошибка при получении списка ответов, мы скоро её исправим.")
        self.options = json.loads(response.content)
        if len(self.options) < 1:
            raise BotException(error="len(self.options) < 1", message="Ошибка при получении списка ответов, мы скоро её исправим.")


    def post_answer(self):
        data = {
            "option": self.options[self.option_choice].get("slug")
        }
        try:
            response = requests.post(url=settings.APP_URL + "api/audit/answer/", headers=self.headers, json=data)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise BotException(error=response.text, message="Ошибка при отправке ответа, мы скоро её исправим.")
