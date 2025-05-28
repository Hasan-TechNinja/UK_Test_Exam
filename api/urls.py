from django.urls import path
from . import views

urlpatterns = [
    path('', views.TheoryView.as_view(), name='theory'),
]
