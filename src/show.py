from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, ParseMode
from telegram.ext import CallbackContext

from src.db import db_session
from src.db.models.attempt import Attempt
from src.db.models.task import Task
from src.general import menu
from src.parse import get_task_by_id
from src.utils import delete_last_message, clean_messages


@delete_last_message
def show_task(update: Update, context: CallbackContext):
    callback = 'show_task'
    context.user_data['one_task'] = True
    task = get_task_by_id(context.user_data['queue'][0])
    if not task:
        update.message.reply_text(f'Не удалось найти задачу №{context.user_data["task_id"]}')
        return menu(update, context)
    text = (f"<b>Задание {task['number'] if task['number'] != 999 else 'прошлых лет'} "
            f"№{task['id']}</b>\n{task['description']}")
    buttons = [[InlineKeyboardButton('Вернуться в меню', callback_data='menu')],
               [InlineKeyboardButton('Пропустить задачу', callback_data='skip_task')]]
    # to be continued
    if not context.user_data.get('delete_on_reload'):
        context.user_data['delete_on_reload'] = []
    if 'images' in task:
        images = task['images'].split(';')
        if len(images) == 1:
            context.user_data['delete_on_reload'].append(
                update.message.reply_photo(images[0], text, reply_markup=markup,
                                           parse_mode=ParseMode.HTML).message_id)
            return callback
        else:
            context.user_data['delete_on_reload'].append(
                [msg.message_id for msg in
                 update.message.reply_media_group([InputMediaPhoto(img) for img in images])])
    context.user_data['delete_on_reload'].append(
        update.message.reply_text(text, reply_markup=markup, parse_mode=ParseMode.HTML).message_id)
    print(f'{context.user_data["delete_on_reload"]=}')
    return callback


def check_answer(update: Update, context: CallbackContext):
    answer = update.message.text.strip()
    with db_session.create_session() as session:
        task = session.query(Task).get(context.user_data['task_id'])
        if not task:
            update.message.reply_text(f'Не удалось проверить ответ на задачу №{context.user_data["task_id"]}')
            return menu(update, context)
        attempt = Attempt(answer=answer, task_id=task.id, user_id=context.user_data['id'],
                          correct=answer == task.answer)
        session.add(attempt)
        session.commit()
        clean_messages()
        # update.message.reply_text('OK' if answer == task.answer else 'Wrong answer')
    context.user_data['queue'].pop(0)
    if context.user_data['queue']:
        return show_task(update, context)
    return menu(update, context)