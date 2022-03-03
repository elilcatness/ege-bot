import json
from json import JSONDecodeError

import requests
from lxml import html
from telegram.error import BadRequest
from telegram.ext import CallbackContext

from src.constants import HEADERS
from src.templates import FILE_PREFIX, IMAGE_PREFIX
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


def process_files_links(text: str):
    states = '<a href="'
    state, i = 0, 0
    while i < len(text):
        s = text[i]
        if text[i] == states[state]:
            state = (state + 1) % len(states)
            if state == 0:
                link = ''
                i += 1
                start = i
                while text[i] != '"':
                    link += text[i]
                    i += 1
                link = FILE_PREFIX % link
                text = text[:start] + link + text[i:]
        else:
            state = 0
        i += 1
    return text


def extract_images_from_text(text: str):
    images = []
    target = '<img'
    try:
        img_idx = text.index('<img')
        while img_idx != -1:
            img_end = img_idx + len(target)
            while text[img_end] != '>':
                img_end += 1
            inner = text[img_idx:img_end + 1]
            target = 'src="'
            src_idx = inner.index(target)
            if src_idx != -1:
                src_idx += len(target)
                src = ''
                while inner[src_idx] != '"':
                    src += inner[src_idx]
                    src_idx += 1
                images.append(IMAGE_PREFIX % src)
            text = text[:img_idx] + text[img_end + 1:]
            img_idx = text.index('<img')
    except ValueError:
        pass
    return text, images


def get_json(url: str, **kwargs):
    response = _get_response(url, **kwargs)
    try:
        assert response
        return response.json()
    except AssertionError:
        return None
    except JSONDecodeError:
        return print(f'Failed to decode JSON from {url}')