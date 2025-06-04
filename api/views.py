from django.shortcuts import render
from main.models import Question, Lesson, Chapter
from . serializers import LessonSerializers, QuestionModelSerializer, ChapterModelSerializer, RegisterSerializer
from rest_framework.views import View, APIView
from rest_framework import mixins, generics, status, viewsets
from rest_framework.response import Response

from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.contrib.auth import authenticate

# # Create your views here.


# -----------------------------------------------Start Authentication----------------------------------
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
    
# --------------------------------------------------End Authentication---------------------------------------------

class QuestionView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionModelSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # lookup_field = 'pk'


class LessonView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializers
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class ChapterView(generics.ListCreateAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterModelSerializer
