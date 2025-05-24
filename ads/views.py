from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import generics, permissions, serializers
from rest_framework.exceptions import PermissionDenied

from .models import Ad, ExchangeProposal
from .forms import AdForm, ExchangeProposalForm
from .serializers import (
    AdSerializer,
    ExchangeProposalSerializer,
    ExchangeProposalCreateSerializer,
    ExchangeProposalUpdateStatusSerializer
)


# --- Веб-интерфейс (Django Class-Based Views) ---
class AdListView(ListView):
    """
    Представление для отображения списка всех активных объявлений.
    """
    model = Ad
    template_name = 'ads/ad_list.html'
    context_object_name = 'page_obj'
    paginate_by = 3 # Добавлена пагинация

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-created_at')
        query = self.request.GET.get('q')
        category = self.request.GET.get('category')
        condition = self.request.GET.get('condition')
        user_param = self.request.GET.get('user')
        my_ads_param = self.request.GET.get('my_ads')

        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(description__icontains=query))
        if category:
            queryset = queryset.filter(category=category)
        if condition:
            queryset = queryset.filter(condition=condition)

        if user_param:
            if user_param == 'me' and self.request.user.is_authenticated:
                queryset = queryset.filter(user=self.request.user)
            else:
                try:
                    user_id_to_filter = int(user_param)
                    queryset = queryset.filter(user__id=user_id_to_filter)
                except (ValueError, TypeError):
                    pass

        if my_ads_param and self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Ad.CATEGORY_CHOICES
        context['conditions'] = Ad.CONDITION_CHOICES

        context['current_query'] = self.request.GET.get('q', '')
        context['current_category'] = self.request.GET.get('category', '')
        context['current_condition'] = self.request.GET.get('condition', '')

        context['current_user_param'] = self.request.GET.get('user', '')
        context['current_my_ads_param'] = self.request.GET.get('my_ads', '')

        context['is_my_ads_filter_active'] = bool(self.request.GET.get('my_ads'))

        return context


class AdDetailView(DetailView):
    """
    Представление для отображения детальной информации об одном объявлении.
    """
    model = Ad
    template_name = 'ads/ad_detail.html'
    context_object_name = 'ad'


class AdCreateView(LoginRequiredMixin, CreateView):
    """
    Представление для создания нового объявления.
    Требует авторизации пользователя (LoginRequiredMixin).
    """
    model = Ad
    form_class = AdForm
    template_name = 'ads/ad_form.html'
    success_url = reverse_lazy('ad_list')

    def form_valid(self, form):
        """
        Переопределяем метод form_valid для автоматического сохранения
        текущего авторизованного пользователя как владельца объявления.
        """
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Создать объявление'
        return context


class AdUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Представление для обновления объявления.
    Требует авторизации пользователя (LoginRequiredMixin).
    """
    model = Ad
    form_class = AdForm
    template_name = 'ads/ad_form.html'
    context_object_name = 'ad'
    success_url = reverse_lazy('ad_list')

    def test_func(self):
        """
        Проверяет, что текущий пользователь является владельцем объявления.
        Это предотвращает редактирование чужих объявлений.
        """
        ad = self.get_object()
        return ad.user == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Редактировать объявление'
        return context


class AdDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Представление для удаления объявления.
    """
    model = Ad
    template_name = 'ads/ad_confirm_delete.html'
    context_object_name = 'ad'
    success_url = reverse_lazy('ad_list')

    def test_func(self):
        """
        Проверяет, что текущий пользователь является владельцем объявления.
        """
        ad = self.get_object()
        return ad.user == self.request.user


class ExchangeProposalCreateView(LoginRequiredMixin, CreateView):
    """
    Представление для создания предложений обмена.
    """
    model = ExchangeProposal
    form_class = ExchangeProposalForm
    template_name = 'ads/exchange_proposal_form.html'

    def get_initial(self):
        initial = super().get_initial()
        ad_receiver_pk = self.kwargs.get('ad_receiver_pk')
        initial['ad_receiver'] = get_object_or_404(Ad, pk=ad_receiver_pk)
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['queryset'] = Ad.objects.filter(user=self.request.user)
        return kwargs

    def form_valid(self, form):
        ad_receiver_pk = self.kwargs.get('ad_receiver_pk')
        ad_receiver = get_object_or_404(Ad, pk=ad_receiver_pk)

        ad_sender = form.cleaned_data['ad_sender']
        if ad_sender.user != self.request.user:
            form.add_error('ad_sender', 'Вы можете отправить предложение только от своего объявления.')
            return self.form_invalid(form)

        form.instance.ad_receiver = ad_receiver
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('exchange_proposal_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ad_receiver'] = get_object_or_404(Ad, pk=self.kwargs.get('ad_receiver_pk'))
        return context


class ExchangeProposalListView(LoginRequiredMixin, ListView):
    """
    Представление для отображения общего списка предложений обмена.
    """
    model = ExchangeProposal
    template_name = 'ads/exchange_proposal_list.html'
    context_object_name = 'proposals'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(Q(ad_sender__user=self.request.user) | Q(ad_receiver__user=self.request.user))

        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sent_proposals'] = self.get_queryset().filter(ad_sender__user=self.request.user)
        context['received_proposals'] = self.get_queryset().filter(ad_receiver__user=self.request.user)
        context['status_choices'] = ExchangeProposal.STATUS_CHOICES
        context['current_status'] = self.request.GET.get('status', '')
        return context


class ExchangeProposalDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Представление для отображения предложения объявлений
    """
    model = ExchangeProposal
    template_name = 'ads/exchange_proposal_detail.html'
    context_object_name = 'proposal'

    def test_func(self):
        proposal = self.get_object()
        return proposal.ad_sender.user == self.request.user or proposal.ad_receiver.user == self.request.user


class ExchangeProposalUpdateStatusView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Представление для обновления предложений обмена.
    """
    model = ExchangeProposal
    fields = ['status']
    template_name = 'ads/exchange_proposal_update_status.html'
    context_object_name = 'proposal'


    def test_func(self):
        proposal = self.get_object()
        return proposal.ad_receiver.user == self.request.user

    def get_success_url(self):
        return reverse_lazy('exchange_proposal_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = ExchangeProposal.STATUS_CHOICES
        return context


# --- REST API (Django REST Framework) ---
class AdListCreateAPIView(generics.ListCreateAPIView):
    """
    API View для просмотра списка всех объявлений и создания новых.
    """
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """
        Переопределяем метод для автоматического сохранения текущего пользователя
        как владельца объявления при его создании через API.
        """
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.query_params.get('q')
        category = self.request.query_params.get('category')
        condition = self.request.query_params.get('condition')

        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(description__icontains=query))
        if category:
            queryset = queryset.filter(category=category)
        if condition:
            queryset = queryset.filter(condition=condition)
        return queryset


class AdDetailUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API View для его обновления или удаления.
    """
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        if self.get_object().user != self.request.user:
            raise PermissionDenied("Вы не являетесь автором этого объявления.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("Вы не являетесь автором этого объявления.")
        instance.delete()


class ExchangeProposalListCreateAPIView(generics.ListCreateAPIView):
    """
    API View для просмотра списка всех предложений обмена и создания новых.
    """
    serializer_class = ExchangeProposalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return ExchangeProposal.objects.filter(
                Q(ad_sender__user=user) | Q(ad_receiver__user=user)
            ).order_by('-created_at')
        return ExchangeProposal.objects.none()

    def perform_create(self, serializer):
        ad_sender_obj = serializer.validated_data['ad_sender']

        if ad_sender_obj.user != self.request.user:
            raise serializers.ValidationError(
                {"ad_sender": "Вы можете отправить предложение только от своего объявления."}
            )
        serializer.save()


class ExchangeProposalDetailAPIView(generics.RetrieveAPIView):
    """
    API View для просмотра конкретного предложения обмена.
    """
    queryset = ExchangeProposal.objects.all()
    serializer_class = ExchangeProposalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if obj.ad_sender.user != self.request.user and obj.ad_receiver.user != self.request.user:
            raise PermissionDenied("У вас нет прав для просмотра этого предложения.")
        return obj


class ExchangeProposalUpdateStatusAPIView(generics.UpdateAPIView):
    """
    API View для обновления статуса предложения обмена.
    """
    queryset = ExchangeProposal.objects.all()
    serializer_class = ExchangeProposalUpdateStatusSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch']

    def perform_update(self, serializer):
        proposal = self.get_object()
        if proposal.ad_receiver.user != self.request.user:
            raise PermissionDenied("Вы можете изменить статус только предложения, адресованного вам.")
        serializer.save()


