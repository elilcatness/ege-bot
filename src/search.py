from telegram import Update
from telegram.ext import CallbackContext

from src.utils import delete_last_message


@delete_last_message
def ask_task_id(update, context: CallbackContext):
    return context.bot.send_message('Введите ID задания'), 'ask_task_id'


@delete_last_message
def search_task(update: Update, context: CallbackContext):
    task_id = update.message.text
    try:
        task_id = int(task_id)
        assert task_id > 0
    except (ValueError, AssertionError):
        update.message.reply_text('ID задачи должен быть представлен в виде натурального числа')
        return ask_task_id(update, context)
    context.user_data['task_id'] = task_id
    return show_task()