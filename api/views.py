from django.shortcuts import render, get_object_or_404

from main.models import Question, Lesson, Chapter, Profile, GuidesSupport, HomePage, GuideSupportContent, LessonContent, UserEvaluation
from . serializers import LessonModelSerializers, QuestionModelSerializer, ChapterModelSerializer, RegisterSerializer, ProfileModelSerializer, GuidesSupportModelSerializer, HomePageModelSerializer, GuideSupportContentModelSerializer, LessonContentModelSerializer, UserEvaluationModelSerializer
# from . permissions import IsAdminOrReadOnly

from rest_framework.views import View, APIView
from rest_framework import mixins, generics, status, viewsets
from rest_framework.response import Response

from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.contrib.auth import authenticate

# # Create your views here.


# -----------------------------------------------Authentication section----------------------------------
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({'message': 'Logout successfully'}, status=status.HTTP_200_OK)
    

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileModelSerializer

    def get_object(self):
        return self.request.user.profile

    
# --------------------------------------------------Admin Control---------------------------------------------

class HomePageAdminView(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
    queryset = HomePage.objects.all()
    serializer_class = HomePageModelSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]


class QuestionAdminView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionModelSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]


class LessonAdminView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonModelSerializers
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    
    
class LessonContentAdminView(generics.ListCreateAPIView):
    queryset = LessonContent.objects.all()
    serializer_class = LessonContentModelSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]


class ChapterAdminView(generics.ListCreateAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterModelSerializer
    permission_classes = [IsAdminUser]


class GuideSupportAdminView(generics.ListCreateAPIView):
    queryset = GuidesSupport.objects.all()
    serializer_class = GuidesSupportModelSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]


class GuideSupportContentAdminView(generics.CreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = GuideSupportContent.objects.all()
    serializer_class = GuideSupportContentModelSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

# --------------------------------------------------Admin details view--------------------------------------
class QuestionDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionModelSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    lookup_field = "pk"

class LessonDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonModelSerializers
    permission_classes = [IsAdminUser]
    lookup_field = "pk"


class LessonContentAdminViewDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LessonContent
    serializer_class = LessonContentModelSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    lookup_field = "pk"


class ChapterDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterModelSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    lookup_field = "pk"

class GuideSupportDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GuidesSupport.objects.all()
    serializer_class = GuidesSupportModelSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    lookup_field = "pk"


# --------------------------------------------------------Study section--------------------------------------
class ChapterListView(APIView):
    def get(self, request):
        chapters = Chapter.objects.all().order_by('id')
        serializer = ChapterModelSerializer(chapters, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ChapterLessonsView(APIView):
    def get(self, request, pk):
        chapter = get_object_or_404(Chapter, id=pk)
        lessons = Lesson.objects.filter(chapter=chapter).reverse()
        serializer = LessonModelSerializers(lessons, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class ChapterLessonDetailView(APIView):
    """
    GET http://127.0.0.1:8000/chapters/1/1/?step=1
    """
    def get(self, request, chapter_id, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id, chapter_id=chapter_id)
        step = int(request.query_params.get('step', 0))
        
        lesson_lists = LessonContent.objects.filter(lesson=lesson).order_by('id')
        
        if step < 0 or step >= lesson_lists.count():
            return Response({"detail": "Invalid step/index."}, status=status.HTTP_404_NOT_FOUND)
    
        current_lesson_list = lesson_lists[step]
        serializer = LessonContentModelSerializer(current_lesson_list)
        
        return Response({
            "step": step,
            "total": lesson_lists.count(),
            "content": serializer.data
        }, status=status.HTTP_200_OK)

    
# -----------------------------------------------------Guides & Support section-------------------------------------
    
class GuideSupportView(APIView):
    """
    GET /api/guides/
    """
    def get(self, request):
        guides = GuidesSupport.objects.all().order_by('id')
        serializer = GuidesSupportModelSerializer(guides, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GuideSupportContentView(APIView):
    """
    GET http://127.0.0.1:8000/guide/1/?step=0
    """
    def get(self, request, guide_id):
        # Get the step index (default = 0)
        try:
            step = int(request.query_params.get("step", 0))
        except (TypeError, ValueError):
            return Response({"detail": "step must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        # Get all contents for this guide
        contents = GuideSupportContent.objects.filter(guide_id=guide_id).order_by("id")
        total = contents.count()

        if total == 0:
            return Response({"detail": "No content for this guide."}, status=status.HTTP_404_NOT_FOUND)

        if step < 0 or step >= total:
            return Response({"detail": "Invalid step index."}, status=status.HTTP_404_NOT_FOUND)

        current_content = contents[step]
        serializer = GuideSupportContentModelSerializer(current_content)

        return Response({
            "step": step,
            "total": total,
            "has_prev": step > 0,
            "has_next": step < total - 1,
            "content": serializer.data
        }, status=status.HTTP_200_OK)


#----------------------------------------------User profile section-----------------------

class UserEvaluationView(APIView):
    def get(self, request, pk):
        evaluation = UserEvaluation.objects.get(user = request.user)
        serializer = UserEvaluationModelSerializer(evaluation)
        return Response(serializer.data, status=status.HTTP_200_OK)