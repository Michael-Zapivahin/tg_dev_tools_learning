from textwrap import dedent

from tg_api import SendMessageRequest, InlineKeyboardMarkup, InlineKeyboardButton
from yostate import Router, Locator
from django.core.paginator import Paginator

from django_tg_bot_framework import (
    PrivateChatStateMachine,
    PrivateChatState,
    PrivateChatMessageReceived,
    PrivateChatCallbackQuery,
)
from django_tg_bot_framework.funnels import AbstractFunnelEvent

from trigger_mailing import funnels as trigger_funnels
from trigger_mailing.state_machine import (
    state_machine as trigger_funnel_state_machine,
    FIRST_MAILING_FUNNEL_SLUG,
    SECOND_MAILING_FUNNEL_SLUG,
)

from .models import Conversation
from .decorators import redirect_menu_commands
from .languages import Languages


def text_locator_state(state_class):

    class WrappedStateClass(state_class):
        def process(self, event):
            state = super().process(event=event)
            SendMessageRequest(
                text=state.state_class_locator,
                chat_id=Conversation.current.tg_chat_id,
            ).send()
    return WrappedStateClass


router = Router(decorators=[redirect_menu_commands, text_locator_state])

state_machine = PrivateChatStateMachine(
    router=router,
    session_model=Conversation,
    context_funcs=[
        trigger_funnel_state_machine.process_collected,
        lambda: AbstractFunnelEvent.set_default_tg_user_id(
            Conversation.current.tg_user_id,
        ),
        *PrivateChatStateMachine.DEFAULT_CONTEXT_FUNCS,
    ],
)


class PaginatorItems:
    def __init__(self, items, per_page):
        self.paginator = Paginator(items, per_page)
        self.current_page = 1
        self.num_pages = self.paginator.num_pages

    def get_current_page_items(self):
        return self.paginator.page(self.current_page)

    def go_to_next_page(self):
        if self.current_page < self.paginator.num_pages:
            self.current_page += 1
        return self.get_current_page_items()

    def go_to_previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
        return self.get_current_page_items()


PAGINATOR_LANGUAGES = PaginatorItems(Languages, 5)


@router.register('/languages/')
class LanguagesState(PrivateChatState):

    def enter_state(self) -> Locator | None:

        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='previous',
                        callback_data='previous',
                    ),
                    InlineKeyboardButton(
                        text='next',
                        callback_data='next',
                    ),
                    InlineKeyboardButton(
                        text='main menu',
                        callback_data='start',
                    ),
                ],
            ],
        )


        SendMessageRequest(
            text=f'The pagination list of languages, of {PAGINATOR_LANGUAGES.num_pages} pages',
            chat_id=Conversation.current.tg_chat_id,
            reply_markup=reply_markup,
        ).send()


    def process_callback_query(self, callback_query: PrivateChatCallbackQuery) -> Locator | None:
        step = callback_query.data
        if step == 'next':
            message = PAGINATOR_LANGUAGES.go_to_next_page().object_list
        elif step == 'previous':
            message = PAGINATOR_LANGUAGES.go_to_previous_page().object_list
        elif step =='start':
            return Locator('/start')
        else:
            message = 'No selected.'

        SendMessageRequest(
            text=f'page {PAGINATOR_LANGUAGES.current_page} {message}',
            chat_id=Conversation.current.tg_chat_id,
        ).send()

        return Locator('/languages/')




@router.register('/buttons/')
class ButtonState(PrivateChatState):

    def enter_state(self) -> Locator | None:
        mailing_text = dedent('''\
            *📨 1️⃣ It's two buttons!*

            Select a button:
        ''')

        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='Button 1',
                        callback_data='button1',
                    ),
                    InlineKeyboardButton(
                        text='Button 2',
                        callback_data='button2',
                    ),
                ],
            ],
        )
        SendMessageRequest(
            text=mailing_text,
            chat_id=Conversation.current.tg_chat_id,
            reply_markup=reply_markup,
        ).send()

    def process_callback_query(self, callback_query: PrivateChatCallbackQuery) -> Locator | None:
        SendMessageRequest(
            text=f'Your choice is: {callback_query.data}',
            chat_id=Conversation.current.tg_chat_id,
        ).send()

        match callback_query.data:
            case 'button1':
                return Locator('/welcome/')
            case 'button2':
                return Locator('/buttons')


@router.register('/')
class FirstUserMessageState(PrivateChatState):
    """Состояние используется для обработки самого первого сообщения пользователя боту.

    Текст стартового сообщения от пользователя игнорируется, а бот переключается в
    следующий стейт, где уже отправит пользователю приветственное сообщение.

    Если вы хотите перекинуть бота в начало диалога -- на "стартовый экран" -- , то используйте другое
    состояние с приветственным сообщением. Это нужно только для обработки первого сообщения от пользователя.
    """

    def process_message_received(self, message: PrivateChatMessageReceived) -> Locator | None:
        # Ignore any user input, redirect to welcome message
        return Locator('/welcome/')


@router.register('/welcome/')
class WelcomeState(PrivateChatState):
    def enter_state(self) -> Locator | None:
        SendMessageRequest(
            text='Welcome!',
            chat_id=Conversation.current.tg_chat_id,
        ).send()

    def process_message_received(self, message: PrivateChatMessageReceived) -> Locator | None:
        SendMessageRequest(
            text=f'Эхо: {message.text}',
            chat_id=Conversation.current.tg_chat_id,
        ).send()
        return Locator('/welcome/')


@router.register('/main-menu/')
class MainMenuState(PrivateChatState):
    def enter_state(self) -> Locator | None:
        SendMessageRequest(
            text='Main Menu',
            chat_id=Conversation.current.tg_chat_id,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text='Go back to welcome message',
                            callback_data='welcome',
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text='Trigger second mailing',
                            callback_data='trigger_second_mailing',
                        ),
                    ],
                ],
            ),
        ).send()

        trigger_funnel_state_machine.push_event(trigger_funnels.LeadNavigatedToMainMenu())

        SendMessageRequest(
            text='First mailing was triggered. Wait for a minute...',
            chat_id=Conversation.current.tg_chat_id,
        ).send()

    def process_callback_query(self, callback_query: PrivateChatCallbackQuery) -> Locator | None:
        match callback_query.data:
            case 'welcome':
                return Locator('/welcome/')
            case 'trigger_second_mailing':
                trigger_funnel_state_machine.push_event(
                    trigger_funnels.LeadLaunchedSecondMailing(),
                )
                SendMessageRequest(
                    text='Second mailing was triggered. Wait for a minute...',
                    chat_id=Conversation.current.tg_chat_id,
                ).send()

    def process_message_received(self, message: PrivateChatMessageReceived) -> Locator | None:
        SendMessageRequest(
            text=f'Эхо: {message.text}',
            chat_id=Conversation.current.tg_chat_id,
        ).send()
        return Locator('/main-menu/')


@router.register('/first-trigger-mailing/')
class FirstTriggerMailingState(PrivateChatState):

    def enter_state(self) -> Locator | None:
        mailing_text = dedent('''\
            *📨 1️⃣ It's a first mailing message!*

            Select an appropriate option:
        ''')

        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='Buy option 1',
                        callback_data='buy_first',
                    ),
                    InlineKeyboardButton(
                        text='Buy option 2',
                        callback_data='buy_second',
                    ),
                    InlineKeyboardButton(
                        text='Stop mailing me',
                        callback_data='stop_mailing',
                    ),
                ],
            ],
        )
        SendMessageRequest(
            text=mailing_text,
            chat_id=Conversation.current.tg_chat_id,
            reply_markup=reply_markup,
        ).send()

        trigger_funnel_state_machine.push_event(trigger_funnels.MailingWasSentToLead(
            funnel_slug=FIRST_MAILING_FUNNEL_SLUG,
        ))

    def process_callback_query(self, callback_query: PrivateChatCallbackQuery) -> Locator | None:
        SendMessageRequest(
            text=f'Your choice is: {callback_query.data}',
            chat_id=Conversation.current.tg_chat_id,
        ).send()

        match callback_query.data:
            case 'buy_first' | 'buy_second':
                trigger_funnel_state_machine.push_event(
                    trigger_funnels.MailingTargetActionAcceptedByLead(
                        action=callback_query.data,
                        funnel_slug=FIRST_MAILING_FUNNEL_SLUG,
                    ),
                )
            case 'stop_mailing':
                trigger_funnel_state_machine.push_event(trigger_funnels.LeadUnsubscribed(
                    funnel_slug=FIRST_MAILING_FUNNEL_SLUG,
                ))


@router.register('/second-trigger-mailing/')
class SecondTriggerMailingState(PrivateChatState):
    def enter_state(self) -> Locator | None:
        mailing_text = dedent('''\
            *📨 2️⃣ It's a second mailing message!*

            Enter /start to return to Main Menu.
        ''')

        SendMessageRequest(
            text=mailing_text,
            chat_id=Conversation.current.tg_chat_id,
        ).send()

        trigger_funnel_state_machine.push_event(trigger_funnels.MailingWasSentToLead(
            funnel_slug=SECOND_MAILING_FUNNEL_SLUG,
        ))
