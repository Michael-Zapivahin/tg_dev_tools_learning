from django import forms

from django.contrib import admin

from django_json_widget.widgets import JSONEditorWidget

from .models import Lead


class LeadAdminForm(forms.ModelForm):
    class Meta:
        widgets = {
            'state_machine_locator': JSONEditorWidget(
                attrs={
                    'style': 'width: 100%; max-width: 1000px; display:inline-block; height:250px;',
                },
            ),
        }


class MailingStatusFilter(admin.SimpleListFilter):
    title = 'Рассылка'
    parameter_name = 'mailing_status'

    def lookups(self, request, model_admin):
        return (
            ('postponed_mailing', '⧖ отложено'),
            ('ready_for_mailing', '▹ готово к отправке'),
            ('failed', '✖ ошибка'),
        )

    def queryset(self, request, queryset):
        match self.value():
            case 'postponed_mailing':
                return queryset.postponed_mailing()
            case 'ready_for_mailing':
                return queryset.ready_for_mailing()
            case 'failed':
                return queryset.mailing_failed()
        return queryset


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = [
        'tg_user_id',
        'get_tg_username',
        'funnel_slug',
        'get_funnel_stage',
        'mailing_failure_reason_code',
    ]
    search_fields = [
        'tg_user_id',
        'mailing_failure_reason_code',
        'mailing_failure_description',
        'mailing_failure_debug_details',
    ]

    readonly_fields = [
        'get_tg_username',
        'get_funnel_stage',
    ]

    form = LeadAdminForm

    list_filter = [
        MailingStatusFilter,
        'funnel_slug',
    ]

    fieldsets = [
        (
            None,
            {
                'fields': [
                    'get_tg_username',
                    'tg_user_id',
                    'funnel_slug',
                ],
            },
        ),
        (
            'Стейт-машина',
            {
                'fields': [
                    'state_machine_locator',
                ],
            },
        ),
        (
            'Ошибки рассылки',
            {
                'fields': [
                    'mailing_failed_at',
                    'mailing_failure_reason_code',
                    'mailing_failure_description',
                    'mailing_failure_debug_details',
                ],
            },
        ),
    ]

    @admin.display(description='Этап воронки', ordering='state_machine_locator__state_class_locator')
    def get_funnel_stage(self, obj):
        return obj.state_machine_locator and obj.state_machine_locator.get('state_class_locator') or ''

    def get_queryset(self, request):
        return super().get_queryset(request).annotate_with_tg_username()

    @admin.display(description='Ник юзера Tg')
    def get_tg_username(self, obj):
        return obj.tg_username or '—'
