from rest_framework import serializers
from main.models import Theory


class TheorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Theory
        # fields = "__all__"
        exclude = ['updated']