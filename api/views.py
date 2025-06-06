from django.shortcuts import render, get_object_or_404

from main.models import Question, Lesson, Chapter, Profile, GuidesSupport
from . serializers import LessonModelSerializers, QuestionModelSerializer, ChapterModelSerializer, RegisterSerializer, ProfileModelSerializer, GuidesSupportModelSerializer
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

class QuestionAdminView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionModelSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    # lookup_field = 'pk'


class LessonAdminView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonModelSerializers
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
        chapter = Chapter.objects.all()
        serializer = ChapterModelSerializer(chapter, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ChapterLessonsView(APIView):
    def get(self, request):
        lesson = Lesson.objects.all()
        serializer = LessonModelSerializers(lesson, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = LessonModelSerializers(data = request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

# class StudyChapterLessonDetails(APIView):
#     def get(self, request, pk):
#         try:
#             chapter = Chapter.objects.get(pk = pk)
#         except Chapter.DoesNotExist:
#             return Response({"detail": "Chapter not found."}, status=status.HTTP_404_NOT_FOUND)

#         lessons = Lesson.objects.filter(chapter=chapter)
#         serializer = LessonModelSerializers(lessons, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

class LessonDetailView(APIView):
    def get(self, request, pk):
        try:
            lesson = Lesson.objects.get(pk=pk)
        except Lesson.DoesNotExist:
            return Response({"detail": "Lesson not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = LessonModelSerializers(lesson)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
# -----------------------------------------------------Guides & Support section-------------------------------------
    
class GuideSupportView(APIView):
    def get(self, request):
        guid = GuidesSupport.objects.all()
        serializer = GuidesSupportModelSerializer(guid, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GuideSupportDetailsView(APIView):
    def get(self, request, pk):
        guid = get_object_or_404(GuidesSupport, pk = pk)
        serializer = GuidesSupportModelSerializer(guid, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)