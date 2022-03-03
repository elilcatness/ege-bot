from telegram import Update, ParseMode, InputMediaPhoto
from telegram.ext import CallbackContext

from src.parse import get_task_by_id
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
    context.user_data['task_id'] = task_id
    return show_task_by_id(update, context)


@delete_last_message
def show_task_by_id(update: Update, context: CallbackContext):
    callback = 'show_task_by_id'
    task = get_task_by_id(context.user_data['task_id'])
    if not task:
        return update.message.reply_text('')
    text = (f"<b>Задание {task['number'] if task['number'] != 999 else 'прошлых лет'} "
            f"№{task['id']}</b>\n{task['description']}")
    send_text = True
    if 'images' in task:
        images = task['images'].split(';')
        if len(images) == 1:
            return update.message.reply_photo(images[0], text, parse_mode=ParseMode.HTML), callback
        else:
            update.message.reply_media_group([InputMediaPhoto(img) for img in images])
    if send_text:
        return update.message.reply_text(text, parse_mode=ParseMode.HTML), callback