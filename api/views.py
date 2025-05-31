from django.shortcuts import render
from main.models import Theory, TheoryCategory
from . serializers import TheoryModelSerializer, TheoryCategorySerializers
from rest_framework.views import View
from rest_framework import mixins, generics, status, viewsets
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


class TheoryDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Theory.objects.all()
    serializer_class = TheoryModelSerializer
    lookup_field = "pk"