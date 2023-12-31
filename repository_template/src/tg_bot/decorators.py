from typing import Type, Any
from yostate import Locator

from django_tg_bot_framework import (
    PrivateChatState,
    PrivateChatMessageReceived,
)


def redirect_menu_commands(state_class: Type[PrivateChatState]) -> Type[PrivateChatState]:
    class WrappedStateClass(state_class):
        def process(self, event: Any) -> Locator:
            if isinstance(event, PrivateChatMessageReceived):
                text = event.text or ''

                match text.split():
                    case ['/start']:
                        return Locator('/main-menu/')
                    case ['/welcome']:
                        return Locator('/welcome/')
                    case['/buttons']:
                        return Locator('/buttons/')
                    case['/languages']:
                        return Locator('/languages/')

            return super().process(event=event)
    return WrappedStateClass
