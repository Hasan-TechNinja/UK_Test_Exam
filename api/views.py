from django.shortcuts import render
from main.models import Question, Lesson, Unit
from . serializers import LessonSerializers, QuestionModelSerializer, UnitModelSerializer
from rest_framework.views import View
from rest_framework import mixins, generics, status, viewsets
# # Create your views here.

# # (Get List and Pust) new Theory 
# class TheoryView(generics.ListCreateAPIView):
#     queryset = Theory.objects.all()
#     serializer_class = TheoryModelSerializer

#     def get(self, request):
#         return self.list(request)

#     def post(self, request):
#         return self.create(request)
    

# # Create Theory Category
# class CategoryCreateView(generics.CreateAPIView):
#     queryset = TheoryCategory.objects.all()
#     serializer_class = TheoryCategorySerializers d

# # (Get Put and Delete) Theory
# class TheoryDetailsView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Theory.objects.all()
#     serializer_class = TheoryModelSerializer
#     lookup_field = "pk"

class QuestionView(generics.CreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionModelSerializer


