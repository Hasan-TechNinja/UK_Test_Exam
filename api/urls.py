from django.urls import path
from . import views

urlpatterns = [
    path('', views.TheoryView.as_view(), name='theory'),
    path('category/create/', views.CategoryCreateView.as_view(), name='categoryCreate'),
    path('theory/<int:pk>/', views.TheoryDetailsView.as_view(), name='theoryDetails'),
]
