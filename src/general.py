from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from src.utils import delete_last_message


@delete_last_message
def menu(update: Update, context: CallbackContext):
    if not context.user_data.get('id'):
        context.user_data['id'] = update.message.from_user.id
    if context.user_data.get('queue'):
        context.user_data['queue'] = []
    markup = InlineKeyboardMarkup([[InlineKeyboardButton('Найти задание по ID', callback_data='search')],
                                   [InlineKeyboardButton(
                                       'Генератор заданий', callback_data='generator')],
                                   [InlineKeyboardButton('Статистика', callback_data='stats')]])
    return context.bot.send_message(context.user_data['id'], 'Меню', reply_markup=markup), 'menu'