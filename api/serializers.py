from rest_framework import serializers
from main.models import Unit, Lesson, Question

class UnitModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        # fields = "__all__"
        exclude = ['updated']

class LessonSerializers(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        exclude = ['user', 'created']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    

class QuestionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"