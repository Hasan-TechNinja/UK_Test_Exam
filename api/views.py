from django.shortcuts import render
from main.models import Theory
from . serializers import TheoryModelSerializer
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