from pydantic import BaseSettings
import httpx
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    tg_token: str
    user_id: str

    class Config:
        env_file = '../.env'
        env_file_encoding = "utf-8"


def send_message(message_text='Hi Michael'):
    app_settings = Settings()
    url = f'https://api.telegram.org/bot{app_settings.tg_token}/sendMessage'
    payload = {
        'chat_id': app_settings.user_id,
        'text': message_text,
    }
    response = httpx.post(url, params=payload)
    response.raise_for_status()


send_message()
