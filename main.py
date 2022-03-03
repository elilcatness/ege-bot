import json
import os
from dotenv import load_dotenv
from telegram import Update, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

from src.db import db_session
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler, CallbackQueryHandler, \
    MessageHandler, Filters

from src.db.models.state import State
from src.db.models.user import User
from src.db.models.task import Task
from src.parse import get_task_by_id
from src.utils import delete_last_message
from src.search import ask_task_id, search_task


def load_states(updater: Updater, conv_handler: ConversationHandler):
    with db_session.create_session() as session:
        for state in session.query(State).all():
            conv_handler._conversations[(state.user_id, state.user_id)] = state.callback
            user_data = json.loads(state.data)
            updater.dispatcher.user_data[state.user_id] = user_data
            context = CallbackContext(updater.dispatcher)
            context._bot = updater.bot


@delete_last_message
def menu(update: Update, context: CallbackContext):
    if not context.user_data.get('id'):
        context.user_data['id'] = update.message.from_user.id
    markup = InlineKeyboardMarkup([[InlineKeyboardButton('Найти задание по ID', callback_data='search')],
                                   [InlineKeyboardButton('Генератор заданий', callback_data='generator')],
                                   [InlineKeyboardButton('Статистика', callback_data='stats')]])
    return context.bot.send_message(context.user_data['id'], 'Меню', reply_markup=markup), 'menu'


# def greet(update: Update, context: CallbackContext):
#     task = get_task_by_id(1041)
#     text = f"<b>Задание {task['number']} №{task['id']}</b>\n{task['description']}"
#     send_text = True
#     if 'images' in task:
#         images = task['images'].split(';')
#         if len(images) == 1:
#             update.message.reply_photo(images[0], text, parse_mode=ParseMode.HTML)
#             send_text = False
#         else:
#             update.message.reply_media_group([InputMediaPhoto(img) for img in images])
#     if send_text:
#         update.message.reply_text(text, parse_mode=ParseMode.HTML)


def main():
    updater = Updater(os.getenv('token'))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', menu)],
        states={
            'menu': [CallbackQueryHandler(ask_task_id, pattern='search')],
            'ask_task_id': [MessageHandler((~Filters.command) & Filters.text, search_task)]
        },
        fallbacks=[CommandHandler('start', menu)]
    )
    updater.dispatcher.add_handler(conv_handler)
    load_states(updater, conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    load_dotenv()
    db_session.global_init(os.getenv('DATABASE_URL'))
    main()
