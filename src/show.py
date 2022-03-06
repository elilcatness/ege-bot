from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, ParseMode
from telegram.ext import CallbackContext

from src.db import db_session
from src.db.models.attempt import Attempt
from src.db.models.task import Task
from src.general import menu
from src.utils import delete_last_message, clean_messages


@delete_last_message
def show_task(update: Update, context: CallbackContext):
    callback = 'show_task'
    with db_session.create_session() as session:
        task_id = context.user_data['queue'][0]
        task = session.query(Task).get(task_id)
        if not task:
            context.bot.send_message(context.user_data['id'], f'Не удалось найти задачу №{task_id}')
            return menu(update, context)
        user_attempts = [att for att in task.attempts if att.user_id == context.user_data['id']]
        buttons = [[InlineKeyboardButton('Вернуться в меню', callback_data='menu')]]
        if len(context.user_data['queue']) > 1:
            buttons[0].append(InlineKeyboardButton('Пропустить задачу', callback_data='skip_task'))
        print(f'{user_attempts=}')
        if user_attempts:
            while len(user_attempts) > 1:
                attempt = user_attempts.pop(0)
                session.delete(attempt)
                session.commit()
            attempt = user_attempts[0]
            attempt_answer = '\n' + attempt.answer if len(attempt.answer.split('\n')) > 1 else attempt.answer
            task_answer = '\n' + task.answer if len(task.answer.split('\n')) > 1 else task.answer
            if context.user_data.get('show_answer'):
                answer_btn_text, callback_data = 'Скрыть правильный ответ', 'hide_answer'
                task_prefix, task_suffix = (('✅', f'\n\n<b>Ответ:</b> {attempt_answer}') if attempt.correct else
                                            ('❌', f'\n\n<b>Последний ответ:</b> {attempt_answer}'
                                             f'\n<b>Правильный ответ: </b> {task_answer}'))
            else:
                answer_btn_text, callback_data = 'Показать правильный ответ', 'show_answer'
                task_prefix, task_suffix = (('✅', '') if attempt.correct else
                                            ('❌', f'\n\n<b>Последний ответ:</b> {attempt_answer}'))
            buttons.append([InlineKeyboardButton(answer_btn_text, callback_data=callback_data)])
        else:
            task_prefix, task_suffix = '', ''
        print(context.user_data)
        text = (f"{task_prefix} <b>Задание {task.number if task.number != 999 else 'прошлых лет'} "
                f"№{task.id}</b>\n{task.description} {task_suffix}")
        markup = InlineKeyboardMarkup(buttons)
        if not context.user_data.get('delete_on_reload'):
            context.user_data['delete_on_reload'] = []
        if task.images:
            images = task.images.split(';')
            if len(images) == 1:
                context.user_data['delete_on_reload'].append(
                    context.bot.send_photo(context.user_data['id'], images[0], text, reply_markup=markup,
                                           parse_mode=ParseMode.HTML).message_id)
                return callback
            else:
                context.user_data['delete_on_reload'].append(
                    [msg.message_id for msg in
                     context.bot.send_media_group(context.user_data['id'],
                                                  [InputMediaPhoto(img) for img in images])])
        context.user_data['delete_on_reload'].append(
            context.bot.send_message(context.user_data['id'], text,
                                     reply_markup=markup, parse_mode=ParseMode.HTML).message_id)
    print(f'{context.user_data["delete_on_reload"]=}')
    return callback


def check_answer(update: Update, context: CallbackContext):
    answer = update.message.text.strip()
    with db_session.create_session() as session:
        task_id = context.user_data['queue'][0]
        task = session.query(Task).get(task_id)
        if not task:
            context.bot.send_message(context.user_data['id'], f'Не удалось проверить ответ на задачу №{task_id}')
            return menu(update, context)
        attempt = Attempt(answer=answer, task_id=task.id, user_id=context.user_data['id'],
                          correct=answer == task.answer)
        session.add(attempt)
        session.commit()
    clean_messages(context)
    return show_task(update, context)


def show_answer(_, context: CallbackContext):
    context.user_data['show_answer'] = True
    clean_messages(context)
    return show_task(_, context)


def hide_answer(_, context: CallbackContext):
    context.user_data['show_answer'] = False
    clean_messages(context)
    return show_task(_, context)