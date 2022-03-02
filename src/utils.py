import json
from json import JSONDecodeError

import requests
from lxml import html
from telegram.error import BadRequest
from telegram.ext import CallbackContext

from constants import HEADERS
from src.db import db_session
from src.db.models.state import State


def delete_last_message(func):
    def wrapper(update, context: CallbackContext):
        if context.user_data.get('message_id'):
            try:
                context.bot.deleteMessage(context.user_data['id'], context.user_data.pop('message_id'))
            except BadRequest:
                pass
        while context.user_data.get('messages_to_delete'):
            context.bot.deleteMessage(context.user_data['id'],
                                      context.user_data['messages_to_delete'].pop(0))
        output = func(update, context)
        if isinstance(output, tuple):
            msg, callback = output
            context.user_data['message_id'] = msg.message_id
            save_state(context.user_data['id'], callback, context.user_data)
        else:
            callback = output
        return callback

    return wrapper


def save_state(user_id: int, callback: str, data: dict):
    with db_session.create_session() as session:
        state = session.query(State).get(user_id)
        str_data = json.dumps(data)
        if state:
            state.user_id = user_id
            state.callback = callback
            state.data = str_data
        else:
            state = State(user_id=user_id, callback=callback, data=str_data)
        session.add(state)
        session.commit()


def _get_response(url: str, **kwargs):
    if 'headers' not in map(str.lower, kwargs.keys()):
        kwargs['headers'] = HEADERS
    response = requests.get(url, **kwargs)
    return response if response else print(f'Failed to get {url}')


def get_doc(url: str, **kwargs):
    response = _get_response(url, **kwargs)
    return html.fromstring(response.text) if response and getattr(response, 'text') else None


def get_json(url: str, **kwargs):
    response = _get_response(url, **kwargs)
    try:
        assert response
        return response.json()
    except AssertionError:
        return None
    except JSONDecodeError:
        return print(f'Failed to decode JSON from {url}')
