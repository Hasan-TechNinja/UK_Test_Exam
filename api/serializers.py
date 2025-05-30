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

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)