from rest_framework import serializers
from main.models import Theory, TheoryCategory

class TheoryModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theory
        # fields = "__all__"
        exclude = ['updated']

class TheoryCategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = TheoryCategory
        exclude = ['user', 'created']