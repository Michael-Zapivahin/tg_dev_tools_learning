#Выявленные проблемы зарепортить в GitLab Issues

#  Отправить себе текстовое сообщение от имени tg-бота  - success
#  Отправить себе текстовое сообщение с кнопками от имени tg-бота - success
#  Отправить себе сообщение с картинкой от имени tg-бота - success
#  сделать ветку и merge

from pydantic import BaseSettings
from dotenv import load_dotenv
from tg_api import (
    SyncTgClient,
    SendMessageRequest,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    SendBytesPhotoRequest,
)

load_dotenv()


class Settings(BaseSettings):
    tg_token: str
    user_id: str

    class Config:
        env_file = '../.env'
        env_file_encoding = "utf-8"


def send_message(token, tg_chat_id):
    with SyncTgClient.setup(token):
        tg_request = SendMessageRequest(chat_id=tg_chat_id, text='Message proofs high level usage.')
        tg_request.send()


def send_message_with_buttons(token, tg_chat_id):
    keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='button_1', callback_data='test'),
            InlineKeyboardButton(text='button_2', callback_data='test'),
        ],
    ],
    )
    with SyncTgClient.setup(token):
        tg_request = SendMessageRequest(
            chat_id=tg_chat_id,
            text='Message proofs keyboard support.',
            reply_markup=keyboard,
        )
        tg_request.send()


def send_message_with_paint(token, chat_id):
    photo_filename = '../epic.png'
    with SyncTgClient.setup(token):
        with open(photo_filename, 'rb') as f:
            photo_content = f.read()
        tg_request = SendBytesPhotoRequest(
            chat_id=chat_id,
            photo=photo_content,
            filename=photo_filename,
            caption='test photo epic.png',
        )
        tg_request.send()


def exec_commands():
    app_settings = Settings()
    send_message_with_paint(app_settings.tg_token, app_settings.user_id)


exec_commands()
