from rest_framework import serializers

from peerinst.models import Question, Teacher


class TeacherSerializer(serializers.ModelSerializer):
    favourite_questions = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Question.objects.all()
    )

    class Meta:
        model = Teacher
        fields = ["favourite_questions"]
