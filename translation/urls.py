from django.urls import path, include

from translation.views import TranslationAPIView
from translation.views import AdminTranslateView

app_name = 'translation'

urlpatterns = [
    path('trnaslate/<str:app_label>/<str:model>/<str:pk>/', AdminTranslateView.as_view(), name='admin-view'),
    path('trnaslate/<str:app_label>/<str:model>/<str:pk>/<str:locale>/', AdminTranslateView.as_view(),
         name='admin-view'),

    path('trnaslate/<str:app_label>/<str:model>/<str:pk>/', TranslationAPIView.as_view(), name='api-view'),
]
