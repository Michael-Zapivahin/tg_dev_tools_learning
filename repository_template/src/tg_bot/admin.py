from django import forms

from django.contrib import admin

from django_json_widget.widgets import JSONEditorWidget

from tg_bot.models import Conversation


class ConversationAdminForm(forms.ModelForm):
    class Meta:
        widgets = {
            'state_machine_locator': JSONEditorWidget(
                attrs={
                    'style': 'width: 100%; max-width: 1000px; display:inline-block; height:250px;',
                },
            ),
        }


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    pass
    list_display = [
        'tg_chat_id',
        'tg_user_id',
        'last_update_tg_username',
        'created_at',
        'interacted_at',
    ]
    date_hierarchy = 'created_at'
    search_fields = [
        'tg_chat_id',
        'tg_user_id',
        'last_update_tg_username',
    ]

    form = ConversationAdminForm
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "tg_chat_id",
                    "tg_user_id",
                    "last_update_tg_username",
                ],
            },
        ),
        (
            "Стейт-машина",
            {
                "fields": [
                    "state_machine_locator",
                ],
            },
        ),
        (
            "Дополнительно",
            {
                "classes": ["collapse"],
                "fields": [
                    "created_at",
                    "interacted_at",
                ],
            },
        ),
    ]
