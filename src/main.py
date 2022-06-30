from . import settings

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
)

from .state import State
from .bot import Bot

def main():

    State.set_handlers({
        State.STEP_START: Bot.start,
        State.STEP_ASK_IS_REGISTERED: Bot.ask_is_registered,
        State.STEP_READ_IS_REGISTERED: Bot.read_is_registered,
        State.STEP_AUTH_ANONYMOUS: Bot.auth_anonymous,
        State.STEP_ASK_USERNAME: Bot.ask_username,
        State.STEP_READ_USERNAME: Bot.read_username,
        State.STEP_ASK_PASSWORD: Bot.ask_password,
        State.STEP_READ_PASSWORD: Bot.read_password,
        State.STEP_AUTH_USER: Bot.auth_user,
        State.STEP_SUGGEST_BIZFUNCS: Bot.suggest_bizfuncs,
        State.STEP_READ_BIZFUNC: Bot.read_bizfunc,
        State.STEP_SUGGEST_QUESTIONS: Bot.suggest_questions,
        State.STEP_READ_QUESTION: Bot.read_question,
        State.STEP_SUGGEST_OPTIONS: Bot.suggest_options,
        State.STEP_READ_OPTION: Bot.read_option,
        State.STEP_WRITE_ANSWER: Bot.write_answer,
        State.STEP_ASK_IS_CONTINUE: Bot.ask_is_continue,
        State.STEP_READ_IS_CONTINUE: Bot.read_is_continue,
    })

    updater = Updater(settings.TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', Bot.start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, Bot.receive_message))

    # Start the Bot
    updater.start_polling()
    updater.idle()
