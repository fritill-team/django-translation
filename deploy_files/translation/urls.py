from django.urls import path, include

from .views import TranslationAPIView, AdminTranslateView

app_name = 'translation'

urlpatterns = [
    path('translate/api/<str:app_label>/<str:model>/<str:pk>/', TranslationAPIView.as_view(),
         name='translate'),
    path('translate/api/<str:app_label>/<str:model>/<str:pk>/<str:locale>/', TranslationAPIView.as_view(),
         name='translate_locale'),
    path('translate/<str:app_label>/<str:model>/<str:pk>/', AdminTranslateView.as_view(), name='translate_form'),
    path('translate/<str:app_label>/<str:model>/<str:pk>/<str:locale>/', AdminTranslateView.as_view(),
         name='translate_form_locale'),
]
