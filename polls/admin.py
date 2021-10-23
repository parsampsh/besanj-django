from django.contrib import admin
from .models import *


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    pass


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    pass
