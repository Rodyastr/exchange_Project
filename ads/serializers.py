from rest_framework import serializers
from .models import Ad, ExchangeProposal
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User.
    Преобразует объекты модели Ad в JSON-формат и наоборот.
    """
    class Meta:
        model = User
        fields = ['id', 'username']

class AdSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Ad.
    """
    user = UserSerializer(read_only=True)

    class Meta:
        model = Ad
        fields = ['id', 'user', 'title', 'description', 'image_url', 'category', 'condition', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

class ExchangeProposalSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели ExchangeProposal.
    """
    ad_sender = serializers.PrimaryKeyRelatedField(queryset=Ad.objects.all())
    ad_receiver = serializers.PrimaryKeyRelatedField(queryset=Ad.objects.all())

    class Meta:
        model = ExchangeProposal
        fields = ['id', 'ad_sender', 'ad_receiver', 'comment', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']

class ExchangeProposalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeProposal
        fields = ['ad_sender', 'ad_receiver', 'comment']

class ExchangeProposalUpdateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeProposal
        fields = ['status']