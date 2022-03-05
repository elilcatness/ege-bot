from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, ParseMode
from telegram.ext import CallbackContext

from src.db import db_session
from src.db.models.task import Task
from src.general import menu
from src.parse import get_task_by_id
from src.utils import delete_last_message


@delete_last_message
def show_task(update: Update, context: CallbackContext):
    callback = 'show_task'
    context.user_data['one_task'] = True
    task = get_task_by_id(context.user_data['task_id'])
    if not task:
        update.message.reply_text(f'Не удалось найти задачу №{context.user_data["task_id"]}')
        return menu(update, context)
    text = (f"<b>Задание {task['number'] if task['number'] != 999 else 'прошлых лет'} "
            f"№{task['id']}</b>\n{task['description']}")
    markup = InlineKeyboardMarkup([[InlineKeyboardButton('Вернуться в меню', callback_data='menu')]])
    if 'images' in task:
        images = task['images'].split(';')
        if len(images) == 1:
            return update.message.reply_photo(images[0], text, reply_markup=markup,
                                              parse_mode=ParseMode.HTML), callback
        else:
            msg = update.message.reply_media_group([InputMediaPhoto(img) for img in images])
            context.user_data['messages_to_delete'] = context.user_data.get('messages_to_delete', []) + [msg]
    return update.message.reply_text(text, reply_markup=markup, parse_mode=ParseMode.HTML), callback


def check_answer(update: Update, context: CallbackContext):
    answer = update.message.text.strip()
    with db_session.create_session() as session:
        task = session.query(Task).get(context.user_data['task_id'])
        if not task:
            update.message.reply_text(f'Не удалось проверить ответ на задачу №{context.user_data["task_id"]}')
            return menu(update, context)
        update.message.reply_text('OK' if answer == task.answer else 'Wrong answer')