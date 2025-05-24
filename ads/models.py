from django.db import models
from django.contrib.auth.models import User

class Ad(models.Model):
    """
    Модель объявления о товаре
    """
    CONDITION_CHOICES = [
        ('new', 'Новый'),
        ('used', 'Б/у'),
        ('good', 'В хорошем состоянии'),
        ('fair', 'Удовлетворительное'),
    ]

    CATEGORY_CHOICES = [
        ('electronics', 'Электроника'),
        ('books', 'Книги'),
        ('clothes', 'Одежда'),
        ('home', 'Товары для дома'),
        ('sport', 'Спорт'),
        ('other', 'Другое'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ads')
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(max_length=255, verbose_name='Описание')
    image_url = models.URLField(blank=True, null=True, verbose_name='Ссылка на изображение')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name='Категория')
    condition = models.CharField(max_length=50, choices=CONDITION_CHOICES, verbose_name='Состояние')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Объявление создано')

    class Meta:
        """
        Мета-опции модели Ad
        """
        ordering = ['-created_at'] # Сортировка по времени создания
        verbose_name = "Объявление"  # Человекочитаемое название модели в единственном числе.
        verbose_name_plural = "Объявления"  # Человекочитаемое название модели во множественном числе.

    def __str__(self):
        """
        Возвращает строковое представление объекта объявления для идентификации объектов.
        """
        return self.title

class ExchangeProposal(models.Model):
    """Модель предложений объявлений"""
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено'),
    ]

    ad_sender = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='sent_proposals', verbose_name='Отправитель')
    ad_receiver = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='received_proposals', verbose_name='Получатель')
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Статус')

    class Meta:
        """
        Мета-опции модели ExchangeProposal.
        """
        unique_together = ('ad_sender', 'ad_receiver')
        ordering = ['-created_at']
        verbose_name = "Предложение обмена"
        verbose_name_plural = "Предложения обмена"

    def __str__(self):
        """
        Возвращает строковое представление объекта предложения обмена.
        """
        return f"Предложение от '{self.ad_sender.title}' к '{self.ad_receiver.title}' ({self.status})"