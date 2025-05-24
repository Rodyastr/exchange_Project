from django.contrib import admin
from .models import Ad, ExchangeProposal

# Register your models here.
@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    """Регистрация модели объявления"""
    list_display = ('user', 'title', 'description',)

@admin.register(ExchangeProposal)
class ExchangeAdmin(admin.ModelAdmin):
    """Регистрация модели обмена объявлений"""
    list_display = ('ad_sender', 'ad_receiver',)