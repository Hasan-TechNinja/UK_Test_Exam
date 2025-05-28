from rest_framework import serializers
from main.models import Theory


class TheoryModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theory
        # fields = "__all__"
        exclude = ['updated']