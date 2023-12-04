from tg_api import Update

from yostate import Locator

from django.conf import settings
from django.urls import path
from django_tg_bot_framework.views import process_webhook_call

from .states import state_machine

app_name = 'tg_bot'


def process_tg_update(update: Update) -> None:
    with state_machine.restore_or_create_session_from_tg_update(update) as session:
        if not session.crawler.attached:
            session.switch_to(Locator('/'))

        session.process_tg_update(update)


urlpatterns = [
    path(
        '',
        process_webhook_call,
        kwargs={
            'webhook_token': settings.ENV.TG.WEBHOOK_TOKEN,
            'process_update': process_tg_update,
        },
        name='process_webhook_call',
    ),
]
