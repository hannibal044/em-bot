import logging

from telegram import (
    Update,
)
from telegram.ext import (
    CallbackContext,
)

from .exceptions import BotException
from .api_auth import AuthAPI
from .api_quiz import QuizAPI
from .state import State

logger = logging.getLogger(__name__)


class Bot:

    def start(update: Update, context: CallbackContext):
        if update.message.text == '/start':
            State.add(update, State.STEP_ASK_IS_REGISTERED)
            State.act(update, context)
        else:
            update.message.reply_text("Чтобы начать, наберите /start")


    def receive_message(update: Update, context: CallbackContext):
        State.act(update, context)


    def ask_is_registered(update: Update, context: CallbackContext):
        update.message.reply_text("Вы зарегистрированы? (y/n)")
        State.set_value(update, 'step', State.STEP_READ_IS_REGISTERED)


    def read_is_registered(update: Update, context: CallbackContext):
        if update.message.text == 'y':
            State.set_value(update, 'step', State.STEP_ASK_USERNAME)
            State.act(update, context)
        elif update.message.text == 'n':
            update.message.reply_text("Создаю для вас гостевую сессию.")
            State.set_value(update, 'step', State.STEP_AUTH_ANONYMOUS)
            State.act(update, context)
        else:
            update.message.reply_text("Извините, не могу понять ваш ответ.")


    def ask_username(update: Update, context: CallbackContext):
        update.message.reply_text("Ваш логин:")
        State.set_value(update, 'step', State.STEP_READ_USERNAME)


    def read_username(update: Update, context: CallbackContext):
        State.set_value(update, 'username', update.message.text)
        State.set_value(update, 'step', State.STEP_ASK_PASSWORD)
        State.act(update, context)


    def ask_password(update: Update, context: CallbackContext):
        update.message.reply_text("Ваш пароль:")
        State.set_value(update, 'step', State.STEP_READ_PASSWORD)


    def read_password(update: Update, context: CallbackContext):
        State.set_value(update, 'password', update.message.text)
        State.set_value(update, 'step', State.STEP_AUTH_USER)
        State.act(update, context)


    def auth_anonymous(update: Update, context: CallbackContext):
        auth = AuthAPI()
        try:
            auth.login_anonymous()
            State.set_value(update, 'token', auth.token)
            update.message.reply_text("Ваш токен: {0}".format(auth.token))
            State.set_value(update, 'step', State.STEP_SUGGEST_BIZFUNCS)
        except BotException as e:
            update.message.reply_text(e.message)
            State.set_value(update, 'step', State.STEP_START)
        State.act(update, context)


    def auth_user(update: Update, context: CallbackContext):
        auth = AuthAPI()
        try:
            auth.login(State.get(update).username, State.get(update).password)
            State.set_value(update, 'token', auth.token)
            update.message.reply_text("Ваш токен: {0}".format(auth.token))
            State.set_value(update, 'step', State.STEP_SUGGEST_BIZFUNCS)
        except BotException as e:
            update.message.reply_text(e.message)
            State.set_value(update, 'step', State.STEP_START)
        State.act(update, context)

    
    def suggest_bizfuncs(update: Update, context: CallbackContext):
        quiz = QuizAPI(State.get(update).token)
        State.set_value(update, 'quiz', quiz)

        try:
            State.get(update).quiz.fetch_bizfuncs()
        except BotException as e:
            update.message.reply_text(e.message)
            State.set_value(update, 'step', State.STEP_START)
            State.act(update, context)
            return

        message = "Выберите бизнес-функцию:\n"
        for idx, bizfunc in enumerate(State.get(update).quiz.bizfuncs):
            message += "{0}. {1}\n".format(idx+1, bizfunc.get("title"))
        update.message.reply_text(message)

        State.set_value(update, 'step', State.STEP_ASK_BIZFUNC)
        State.act(update, context)


    def ask_bizfunc(update: Update, context: CallbackContext):
        message = "Ваш выбор (1-{0}): ".format(len(State.get(update).quiz.bizfuncs))
        update.message.reply_text(message)
        State.set_value(update, 'step', State.STEP_READ_BIZFUNC)


    def read_bizfunc(update: Update, context: CallbackContext):
        try:
            choice = int(update.message.text)-1
        except ValueError:
            choice = -1
        if choice < 0 or choice >= len(State.get(update).quiz.bizfuncs):
            update.message.reply_text("Недопустимое значение")
        else:
            State.get(update).quiz.bizfunc_choice = choice
            State.set_value(update, 'step', State.STEP_SUGGEST_QUESTIONS)
            State.act(update, context)


    def suggest_questions(update: Update, context: CallbackContext):
        try:
            State.get(update).quiz.fetch_questions()
        except BotException as e:
            update.message.reply_text(e.message)
            State.set_value(update, 'step', State.STEP_SUGGEST_BIZFUNCS)
            State.act(update, context)
            return

        message = "Выберите вопрос:\n"
        for idx, question in enumerate(State.get(update).quiz.questions):
            message += "{0}. {1}\n".format(idx+1, question.get("text"))
        update.message.reply_text(message)

        State.set_value(update, 'step', State.STEP_ASK_QUESTION)
        State.act(update, context)


    def ask_question(update: Update, context: CallbackContext):
        message = "Ваш выбор (1-{0}): ".format(len(State.get(update).quiz.questions))
        update.message.reply_text(message)
        State.set_value(update, 'step', State.STEP_READ_QUESTION)


    def read_question(update: Update, context: CallbackContext):
        try:
            choice = int(update.message.text)-1
        except ValueError:
            choice = -1
        if choice < 0 or choice >= len(State.get(update).quiz.questions):
            update.message.reply_text("Недопустимое значение")
        else:
            State.get(update).quiz.question_choice = choice
            State.set_value(update, 'step', State.STEP_SUGGEST_OPTIONS)
            State.act(update, context)


    def suggest_options(update: Update, context: CallbackContext):
        try:
            State.get(update).quiz.fetch_options()
        except BotException as e:
            update.message.reply_text(e.message)
            State.set_value(update, 'step', State.STEP_SUGGEST_BIZFUNCS)
            State.act(update, context)
            return

        message = "Выберите вариант ответа:\n"
        for idx, option in enumerate(State.get(update).quiz.options):
            message += "{0}. {1}\n".format(idx+1, option.get("text"))
        update.message.reply_text(message)

        State.set_value(update, 'step', State.STEP_ASK_OPTION)
        State.act(update, context)


    def ask_option(update: Update, context: CallbackContext):
        message = "Ваш выбор (1-{0}): ".format(len(State.get(update).quiz.options))
        update.message.reply_text(message)
        State.set_value(update, 'step', State.STEP_READ_OPTION)


    def read_option(update: Update, context: CallbackContext):
        try:
            choice = int(update.message.text)-1
        except ValueError:
            choice = -1
        if choice < 0 or choice >= len(State.get(update).quiz.options):
            update.message.reply_text("Недопустимое значение")
        else:
            State.get(update).quiz.option_choice = choice
            State.set_value(update, 'step', State.STEP_WRITE_ANSWER)
            State.act(update, context)


    def write_answer(update: Update, context: CallbackContext):
        try:
            State.get(update).quiz.post_answer()
        except BotException as e:
            update.message.reply_text(e.message)
            State.set_value(update, 'step', State.STEP_SUGGEST_BIZFUNCS)
            State.act(update, context)
            return

        update.message.reply_text("Спасибо! Комментарий к ответу:")
        update.message.reply_text(State.get(update).quiz.options[State.get(update).quiz.option_choice].get("solution"))
        State.set_value(update, 'step', State.STEP_ASK_IS_CONTINUE)
        State.act(update, context)


    def ask_is_continue(update: Update, context: CallbackContext):
        update.message.reply_text("Хотите продолжить? (y/n)")
        State.set_value(update, 'step', State.STEP_READ_IS_CONTINUE)


    def read_is_continue(update: Update, context: CallbackContext):
        if update.message.text == 'y':
            State.set_value(update, 'step', State.STEP_SUGGEST_BIZFUNCS)
            State.act(update, context)
        elif update.message.text == 'n':
            update.message.reply_text("Хорошо! Если что, снова наберите /start")
        else:
            update.message.reply_text("Извините, не могу понять ваш ответ.")
