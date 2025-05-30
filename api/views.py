from django.shortcuts import render
from main.models import Theory, TheoryCategory
from . serializers import TheoryModelSerializer, TheoryCategorySerializers
from rest_framework.views import View
from rest_framework import mixins, generics
# Create your views here.

class TheoryView(generics.RetrieveDestroyAPIView, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = Theory.objects.all()
    serializer_class = TheoryModelSerializer

    def get(self, request):
        return self.list(request)

    def post(self, request):
        return self.create(request)
    

class CategoryCreateView(generics.CreateAPIView):
    queryset = TheoryCategory.objects.all()
    serializer_class = TheoryCategorySerializers

    # def post(self, request):
    #     return self.create(request)