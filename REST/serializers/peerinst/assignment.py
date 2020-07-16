import bleach

from django.contrib.auth.models import User
from django.template.defaultfilters import title
from rest_framework import serializers

from peerinst.models import (
    Assignment,
    AssignmentQuestions,
    Discipline,
    Question,
)
from peerinst.templatetags.bleach_html import ALLOWED_TAGS


class DisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discipline
        fields = ["title"]

    def to_representation(self, instance):
        """Bleach HTML-supported fields"""
        ret = super().to_representation(instance)
        ret["title"] = bleach.clean(
            ret["title"], tags=[], styles=[], strip=True
        )
        ret["title"] = title(ret["title"])
        return ret


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username"]


class QuestionSerializer(serializers.ModelSerializer):
    answer_count = serializers.SerializerMethodField()
    discipline = DisciplineSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    def get_answer_count(self, obj):
        return obj.answer_set.count()

    class Meta:
        model = Question
        fields = ["pk", "title", "text", "user", "discipline", "answer_count"]

    def to_representation(self, instance):
        """Bleach HTML-supported fields"""
        ret = super().to_representation(instance)
        ret["title"] = bleach.clean(
            ret["title"], tags=ALLOWED_TAGS, styles=[], strip=True
        )
        ret["text"] = bleach.clean(
            ret["text"], tags=ALLOWED_TAGS, styles=[], strip=True
        )
        return ret


class RankSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)

    class Meta:
        model = AssignmentQuestions
        fields = ["question", "rank"]


class AssignmentSerializer(serializers.ModelSerializer):
    questions = RankSerializer(
        source="assignmentquestions_set", many=True, read_only=True
    )

    class Meta:
        model = Assignment
        fields = ["title", "questions"]
