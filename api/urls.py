from django.urls import path
from . import views
from .views import RegisterView, LoginView, LogoutView

urlpatterns = [
    path('question/', views.QuestionView.as_view(), name='theory'),
    path('lesson/', views.LessonView.as_view(), name='lesson'),
    path('unit/', views.UnitView.as_view(), name='unit'),
    path('register/', RegisterView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
