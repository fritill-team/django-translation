from django.urls import path, include

from translation.views import AdminTranslateView

app_name = 'translation'

urlpatterns = [
    path('trnaslate/<str:app_label>/<str:model>/<str:pk>/', AdminTranslateView.as_view(), name='translate'),
    path('trnaslate/<str:app_label>/<str:model>/<str:pk>/<str:locale>/', AdminTranslateView.as_view(),
         name='translate'),
]
