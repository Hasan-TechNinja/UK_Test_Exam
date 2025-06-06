from django.urls import path
from . import views

urlpatterns = [
    # admin
    path('questionAdmin/', views.QuestionAdminView.as_view(), name='theoryAdmin'),
    path('lessonAdmin/', views.LessonAdminView.as_view(), name='lessonAdmin'),
    path('chapterAdmin/', views.ChapterAdminView.as_view(), name='chapterAdmin'),
    path('guidAdmin/', views.GuideSupportAdminView.as_view(), name='guidAdmin'),

    # authentication
    path('register/', views.RegisterView.as_view(), name='registration'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),

    # user 
    path('chapters/', views.ChapterListView.as_view(), name="chapters"),
    path('lessons/', views.ChapterLessonsView.as_view(), name="lessons"),
    path('lessonDetails/<int:pk>', views.LessonDetailView.as_view(), name='lessonDetails'),
    path('guid/', views.GuideSupportView.as_view(), name='guid'),
    path('guid/<int:pk>', views.GuidSupportDetailsView.as_view(), name='guidDetails'),
]
