from django.contrib import admin

from .models import Mailing, MailingAttempt, Message, Recipient


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "date_added")
    list_filter = ("date_added",)
    search_fields = ("email", "full_name", "comment")
    date_hierarchy = "date_added"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "body")
    list_filter = ("subject",)
    search_fields = ("subject", "body")


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "start_time", "end_time", "status")
    list_filter = ("status", "start_time", "end_time")
    search_fields = ("message__subject",)
    date_hierarchy = "start_time"
    filter_horizontal = ("recipients",)


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "mailing", "timestamp", "status", "server_response_short")
    list_filter = ("status", "timestamp", "mailing")
    search_fields = ("mailing__message__subject", "server_response")
    date_hierarchy = "timestamp"
    readonly_fields = ("timestamp",)
    # filter_horizontal = ('recipients',)

    def server_response_short(self, obj):
        if obj.server_response:
            return obj.server_response[:50] + "..." if len(obj.server_response) > 50 else obj.server_response
        return "-"

    server_response_short.short_description = "Ответ сервера"
