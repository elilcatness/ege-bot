import json
import os
from dotenv import load_dotenv

from src.db import db_session
from telegram.ext import (Updater, CommandHandler, CallbackContext, ConversationHandler, CallbackQueryHandler,
                          MessageHandler, Filters)

from src.db.models.state import State
from src.db.models.task import Task
from src.show import check_answer
from src.general import menu
from src.parse import get_tasks_by_number
from src.search import ask_task_id, search_task


def load_data(_):
    with db_session.create_session() as session:
        for n in range(1, 28):
            tasks = get_tasks_by_number(n)
            for task_d in tasks[::-1]:
                task = session.query(Task).get(task_d['id'])
                if not task:
                    task = Task(**task_d)
                    session.add(task)
                    session.commit()
                else:
                    if task.description != task_d['description']:
                        task.description = task_d['description']
                    if task.answer != task_d['answer']:
                        task.answer = task_d['answer']
                    session.add(task)
                    session.commit()
                print(task)


def load_states(updater: Updater, conv_handler: ConversationHandler):
    # context = CallbackContext(updater.dispatcher)
    # context.job_queue.run_once(load_data, 0)
    with db_session.create_session() as session:
        for state in session.query(State).all():
            conv_handler._conversations[(
                state.user_id, state.user_id)] = state.callback
            user_data = json.loads(state.data)
            updater.dispatcher.user_data[state.user_id] = user_data
            context = CallbackContext(updater.dispatcher)
            context._bot = updater.bot


def main():
    updater = Updater(os.getenv('token'))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', menu)],
        states={
            'menu': [CallbackQueryHandler(ask_task_id, pattern='search')],
            'ask_task_id': [MessageHandler((~Filters.command) & Filters.text, search_task)],
            'show_task': [MessageHandler((~Filters.command) & Filters.text, check_answer)]
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
