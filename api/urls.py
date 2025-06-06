from django.urls import path
from . import views

urlpatterns = [
    # admin
    path('questionAdmin/', views.QuestionAdminView.as_view(), name='theoryAdmin'),
    path('lessonAdmin/', views.LessonAdminView.as_view(), name='lessonAdmin'),
    path('chapterAdmin/', views.ChapterAdminView.as_view(), name='chapterAdmin'),
    path('guideAdmin/', views.GuideSupportAdminView.as_view(), name='guideAdmin'),
    
    path('guideAdmin/<int:pk>', views.GuideSupportDetailsAdminView.as_view(), name='guideAdmin'),
    path('chapterAdmin/<int:pk>', views.ChapterDetailsAdminView.as_view(), name='chapterAdmin'),
    path('lessonAdmin/<int:pk>', views.LessonDetailsAdminView.as_view(), name='lessonAdmin'),
    path('questionAdmin/<int:pk>', views.QuestionDetailsAdminView.as_view(), name='questionAdmin'),

    # authentication
    path('register/', views.RegisterView.as_view(), name='registration'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),

    # user 
    path('chapters/', views.ChapterListView.as_view(), name="chapters"),
    path('lessons/', views.ChapterLessonsView.as_view(), name="lessons"),
    path('lessonDetails/<int:pk>', views.LessonDetailView.as_view(), name='lessonDetails'),
    path('guide/', views.GuideSupportView.as_view(), name='guid'),
    path('guide/<int:pk>/', views.GuideSupportDetailsView.as_view(), name='guideDetails'),
]
