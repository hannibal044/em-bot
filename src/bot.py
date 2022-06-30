import logging

from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton,
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
        button_list = [
            [
                KeyboardButton('Да'), KeyboardButton('Нет')
            ]
        ]
        reply_markup = ReplyKeyboardMarkup(button_list, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text("Вы зарегистрированы?", reply_markup=reply_markup)
        State.set_value(update, 'step', State.STEP_READ_IS_REGISTERED)


    def read_is_registered(update: Update, context: CallbackContext):
        if update.message.text == 'Да':
            State.set_value(update, 'step', State.STEP_ASK_USERNAME)
            State.act(update, context)
        elif update.message.text == 'Нет':
            update.message.reply_text("Создаю для вас гостевую сессию.")
            State.set_value(update, 'step', State.STEP_AUTH_ANONYMOUS)
            State.act(update, context)
        else:
            update.message.reply_text("Извините, не могу понять ваш ответ.")
            State.act(update, context)

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
        global list_biz
        quiz = QuizAPI(State.get(update).token)
        State.set_value(update, 'quiz', quiz)

        try:
            State.get(update).quiz.fetch_bizfuncs()
        except BotException as e:
            update.message.reply_text(e.message)
            State.set_value(update, 'step', State.STEP_START)
            State.act(update, context)
            return

        list_biz = []
        for bizfunc in State.get(update).quiz.bizfuncs:
            list_biz.append(bizfunc.get("title"))
        button_biz = []
        for i in list_biz:
            button_biz.append([KeyboardButton(i)])
        reply_markup = ReplyKeyboardMarkup(button_biz, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text('Выберите бизнес-функцию', reply_markup=reply_markup)
        State.set_value(update, 'step', State.STEP_READ_BIZFUNC)

    def read_bizfunc(update: Update, context: CallbackContext):
        try:
            choice = list_biz.index(update.message.text)
        except ValueError:
            choice = -1
        if choice < 0 or choice >= len(State.get(update).quiz.bizfuncs):
            update.callback_query.message.reply_text("Недопустимое значение")
        else:
            State.get(update).quiz.bizfunc_choice = choice
            State.set_value(update, 'step', State.STEP_SUGGEST_QUESTIONS)
            State.act(update, context)

    def suggest_questions(update: Update, context: CallbackContext):
        global list_questions
        try:
            State.get(update).quiz.fetch_questions()
        except BotException as e:
            update.message.reply_text(e.message)
            State.set_value(update, 'step', State.STEP_SUGGEST_BIZFUNCS)
            State.act(update, context)
            return
        list_questions = []
        for questfunc in State.get(update).quiz.questions:
            list_questions.append(questfunc.get("text"))
        button_questions = []
        for i in list_questions:
            button_questions.append([KeyboardButton(i)])
        reply_markup = ReplyKeyboardMarkup(button_questions, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text('Выберите вопрос', reply_markup=reply_markup)
        State.set_value(update, 'step', State.STEP_ASK_QUESTION)
        State.act(update, context)

    def read_question(update: Update, context: CallbackContext):
        try:
            choice = list_questions.index(update.message.text)
        except ValueError:
            choice = -1
        if choice < 0 or choice >= len(State.get(update).quiz.questions):
            update.message.reply_text("Недопустимое значение")
        else:
            State.get(update).quiz.question_choice = choice
            State.set_value(update, 'step', State.STEP_SUGGEST_OPTIONS)
            State.act(update, context)

    def suggest_options(update: Update, context: CallbackContext):
        global list_options
        try:
            State.get(update).quiz.fetch_options()
        except BotException as e:
            update.message.reply_text(e.message)
            State.set_value(update, 'step', State.STEP_SUGGEST_BIZFUNCS)
            State.act(update, context)
            return
        list_options = []
        for optfunc in State.get(update).quiz.options:
            list_options.append(optfunc.get("text"))
        button_options = []
        for i in list_options:
            button_options.append([KeyboardButton(i)])
        reply_markup = ReplyKeyboardMarkup(button_options, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text('Выберите вариант ответа', reply_markup=reply_markup)

        State.set_value(update, 'step', State.STEP_ASK_OPTION)
        State.act(update, context)

    def read_option(update: Update, context: CallbackContext):
        try:
            choice = list_options.index(update.message.text)
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
        button_list = [
            [
                KeyboardButton('Да'), KeyboardButton('Нет')
            ]
        ]
        reply_markup = ReplyKeyboardMarkup(button_list, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text("Хотите продолжить?", reply_markup=reply_markup)
        State.set_value(update, 'step', State.STEP_READ_IS_CONTINUE)

    def read_is_continue(update: Update, context: CallbackContext):
        if update.message.text == 'Да':
            State.set_value(update, 'step', State.STEP_SUGGEST_BIZFUNCS)
            State.act(update, context)
        elif update.message.text == 'Нет':
            update.message.reply_text("Хорошо! Если что, снова наберите /start")
        else:
            update.message.reply_text("Извините, не могу понять ваш ответ.")
