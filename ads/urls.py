from django.urls import path
from . import views
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

urlpatterns = [
    # --- Веб-интерфейс ---
    path('', views.AdListView.as_view(), name='ad_list'),
    path('ads/create/', views.AdCreateView.as_view(), name='ad_create'),
    path('ads/<int:pk>/', views.AdDetailView.as_view(), name='ad_detail'),
    path('ads/<int:pk>/edit/', views.AdUpdateView.as_view(), name='ad_edit'),
    path('ads/<int:pk>/delete/', views.AdDeleteView.as_view(), name='ad_delete'),

    path('proposals/', views.ExchangeProposalListView.as_view(), name='exchange_proposal_list'),
    path('proposals/<int:pk>/', views.ExchangeProposalDetailView.as_view(), name='exchange_proposal_detail'),
    path('proposals/create/<int:ad_receiver_pk>/', views.ExchangeProposalCreateView.as_view(), name='exchange_proposal_create'),
    path('proposals/<int:pk>/update_status/', views.ExchangeProposalUpdateStatusView.as_view(), name='exchange_proposal_update_status'),

    # --- REST API ---
    path('api/ads/', views.AdListCreateAPIView.as_view(), name='api_ad_list_create'),
    path('api/ads/<int:pk>/', views.AdDetailUpdateDeleteAPIView.as_view(), name='api_ad_detail_update_delete'),
    path('api/proposals/', views.ExchangeProposalListCreateAPIView.as_view(), name='api_exchange_proposal_list_create'),
    path('api/proposals/<int:pk>/', views.ExchangeProposalDetailAPIView.as_view(), name='api_exchange_proposal_detail'),
    path('api/proposals/<int:pk>/status/', views.ExchangeProposalUpdateStatusAPIView.as_view(), name='api_exchange_proposal_update_status'),

    # --- Schema ---
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]