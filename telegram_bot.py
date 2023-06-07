from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from bot.core import CoreSession
import config.config as config
import logging

logger = logging.getLogger('Telegram frontend')
core = CoreSession()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    instruction = '''
    Чтобы очистить контекст диалога напишите команду - /clear
    Автор - https://t.me/chckdskeasfsd
    Внимание!!!
    1. Автор не несет ответственности за ответы нейронной сети
    2. Вы сами это используете, все вопросы к вам.
    3. openAI - кринж
    '''
    await update.message.reply_text(instruction)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = int(update.message.chat_id)
    message = update.message.text
    core.add_user_message(user_id, message)
    answer = core.process_user_message(user_id)
    core.add_bot_message(user_id, answer)
    core.truncate_context(user_id)
    logger.info('User = [{}]'.format(user_id))
    logger.info('Message = [{}]'.format(message))
    logger.info('Answer = [{}]'.format(answer))
    logger.info('-' * 20)
    await update.message.reply_text(answer)


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = int(update.message.chat_id)
    core.clear_context(user_id)
    await update.message.reply_text('Контекст очищен')


def main():
    application = Application.builder().token(config.tgbot_token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clear", clear))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.run_polling()


if __name__ == "__main__":
    main()
