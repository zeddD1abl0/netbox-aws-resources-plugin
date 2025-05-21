from django.contrib import admin

from .models import AWSAccount


@admin.register(AWSAccount)
class AWSAccountAdmin(admin.ModelAdmin):
    list_display = ("account_id", "name", "tenant")
    list_filter = ("tenant",)
    search_fields = ("account_id", "name")
