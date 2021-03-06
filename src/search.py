from telegram import Update  # , ParseMode, InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from src.show import show_task
# from src.parse import get_task_by_id
from src.utils import delete_last_message


@delete_last_message
def ask_task_id(_, context: CallbackContext):
    return context.bot.send_message(context.user_data['id'], 'Введите ID задания'), 'ask_task_id'


@delete_last_message
def search_task(update: Update, context: CallbackContext):
    task_id = update.message.text
    try:
        task_id = int(task_id)
        assert task_id > 0
    except (ValueError, AssertionError):
        update.message.reply_text('ID задачи должен быть представлен в виде натурального числа')
        return ask_task_id(update, context)
    context.user_data['queue'] = context.user_data.get('queue', []) + [task_id]
    return show_task(update, context)