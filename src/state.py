import logging

from telegram import Update
from telegram.ext import CallbackContext

from .exceptions import BotException

logger = logging.getLogger(__name__)

states = {}


class State:

    STEP_START = 'start'
    STEP_ASK_IS_REGISTERED = 'ask_is_registered'
    STEP_READ_IS_REGISTERED = 'read_is_registered'
    STEP_AUTH_ANONYMOUS = 'auth_anonymous'
    STEP_ASK_USERNAME = 'auth_ask_username'
    STEP_READ_USERNAME = 'read_username'
    STEP_ASK_PASSWORD = 'ask_password'
    STEP_READ_PASSWORD = 'read_password'
    STEP_AUTH_USER = "auth_user"
    STEP_SUGGEST_BIZFUNCS = "suggest_bizfuncs"
    STEP_ASK_BIZFUNC = "ask_bizfunc",
    STEP_READ_BIZFUNC = "read_bizfunc",
    STEP_SUGGEST_QUESTIONS = "suggest_questions"
    STEP_ASK_QUESTION = "ask_question"
    STEP_READ_QUESTION = "read_question"
    STEP_SUGGEST_OPTIONS = "suggest_options"
    STEP_ASK_OPTION = "ask_option"
    STEP_READ_OPTION = "read_option"
    STEP_WRITE_ANSWER = "write_answer"
    STEP_ASK_IS_CONTINUE = "ask_is_continue"
    STEP_READ_IS_CONTINUE = "read_is_continue"

    @classmethod
    def set_handlers(cls, handlers):
        cls.handlers = handlers

    @classmethod
    def add(cls, update: Update, step):
        state = State()
        setattr(state, 'step', step)
        states[update.effective_chat.id] = state

    @classmethod
    def set_value(cls, update: Update, attr, value):
        setattr(cls.get(update), attr, value)

    @classmethod
    def get(cls, update: Update):
        if not update.effective_chat.id in states:
            cls.add(update, cls.STEP_START)
        return states[update.effective_chat.id]

    @classmethod
    def act(cls, update: Update, context: CallbackContext):
        step = cls.get(update).step
        try:
            cls.handlers[step](update, context)
        except BotException as e:
            pass
