from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from bot.core import CoreSession
import config.config as config
import logging

logger = logging.getLogger('Telegram frontend')
core = CoreSession()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = int(update.message.chat_id)
    core.set_system_prompt(user_id, 'Ты девушка Анфиса, разговаривающая с незнакомым человеком.')
    instruction = '''
Автор - https://t.me/chckdskeasfsd
Github: https://github.com/Den4ikAI/Anfice-chatbot
Внимание!!!
1. Автор не несет ответственности за ответы нейронной сети
2. Вы сами это используете, все вопросы к вам.
3. openAI - кринж

Список доступных команд:
/clear - очистка контекста диалога
/help - вызов данного сообщения
/default - режим по умолчанию
/wife - режим заботливой жены
/girlfriend - режим девушки
/philosopher - режим философа
/psychologist - режим психолога (может работать нестабильно)
'''
    await update.message.reply_text(instruction)

async def helper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    instruction = '''
Автор - https://t.me/chckdskeasfsd
Github: https://github.com/Den4ikAI/Anfice-chatbot
Внимание!!!
1. Автор не несет ответственности за ответы нейронной сети
2. Вы сами это используете, все вопросы к вам.
3. openAI - кринж

Список доступных команд:
/clear - очистка контекста диалога
/help - вызов данного сообщения
/default - режим по умолчанию
/wife - режим заботливой жены
/girlfriend - режим девушки
/philosopher - режим философа
/psychologist - режим психолога (может работать нестабильно)
'''
    await update.message.reply_text(instruction)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = int(update.message.chat_id)
    message = update.message.text
    core.add_user_message(user_id, message)
    answer = core.process_user_message(user_id)
    core.add_bot_message(user_id, answer)
    logger.info('User = [{}]'.format(user_id))
    logger.info('Message = [{}]'.format(message))
    logger.info('Answer = [{}]'.format(answer))
    logger.info('-' * 20)
    await update.message.reply_text(answer)


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = int(update.message.chat_id)
    core.clear_context(user_id)
    await update.message.reply_text('Контекст очищен')

async def wife(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = int(update.message.chat_id)
    core.set_system_prompt(user_id, 'Ты заботливая жена, говоришь со своим мужем.')
    await update.message.reply_text('Режим заботливая жена установлен!')

async def girlfriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = int(update.message.chat_id)
    core.set_system_prompt(user_id, 'Ты девушка, говоришь со своим любимым парнем.')
    await update.message.reply_text('Режим девушки установлен!')

async def philosopher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = int(update.message.chat_id)
    core.set_system_prompt(user_id, 'Ты философ, любящий рассуждать.')
    await update.message.reply_text('Режим философа установлен!')

async def psychologist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = int(update.message.chat_id)
    core.set_system_prompt(user_id, 'Ты психолог говорящий с пациентом.')
    await update.message.reply_text('Режим психолога установлен! Внимание! Данный режим может работать нестабильно!')

async def default(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = int(update.message.chat_id)
    core.set_system_prompt(user_id, 'Ты девушка Анфиса, разговаривающая с незнакомым человеком.')
    await update.message.reply_text('Режим по умолчанию установлен!')


def main():
    application = Application.builder().token(config.tgbot_token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", helper))
    application.add_handler(CommandHandler("wife", wife))
    application.add_handler(CommandHandler("girlfriend", girlfriend))
    application.add_handler(CommandHandler("philosopher", philosopher))
    application.add_handler(CommandHandler("psychologist", psychologist))
    application.add_handler(CommandHandler("default", default))
    application.add_handler(CommandHandler("clear", clear))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.run_polling()


if __name__ == "__main__":
    main()
