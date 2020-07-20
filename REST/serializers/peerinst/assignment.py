import bleach

from django.contrib.auth.models import User
from django.template.defaultfilters import title
from rest_framework import serializers

from peerinst.models import (
    Assignment,
    AssignmentQuestions,
    Category,
    Discipline,
    Question,
)
from peerinst.templatetags.bleach_html import ALLOWED_TAGS


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["title"]

    def to_representation(self, instance):
        """Bleach and ensure title case"""
        ret = super().to_representation(instance)
        ret["title"] = bleach.clean(
            ret["title"], tags=[], styles=[], strip=True
        )
        ret["title"] = title(ret["title"])
        return ret


class DisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discipline
        fields = ["title"]

    def to_representation(self, instance):
        """Bleach and ensure title case"""
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
    category = CategorySerializer(many=True, read_only=True)
    choices = serializers.SerializerMethodField()
    discipline = DisciplineSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    most_convincing_rationales = serializers.SerializerMethodField()
    matrix = serializers.SerializerMethodField()

    def get_answer_count(self, obj):
        return obj.answer_set.count()

    def get_choices(self, obj):
        return obj.get_choices()

    def get_most_convincing_rationales(self, obj):
        return obj.get_most_convincing_rationales()

    def get_matrix(self, obj):
        return obj.get_matrix()

    class Meta:
        model = Question
        fields = [
            "pk",
            "title",
            "text",
            "user",
            "discipline",
            "answer_count",
            "category",
            "image",
            "image_alt_text",
            "choices",
            "most_convincing_rationales",
            "matrix",
        ]

    def to_representation(self, instance):
        """Bleach HTML-supported fields"""
        ret = super().to_representation(instance)
        ret["title"] = bleach.clean(
            ret["title"], tags=ALLOWED_TAGS, styles=[], strip=True
        )
        ret["text"] = bleach.clean(
            ret["text"], tags=ALLOWED_TAGS, styles=[], strip=True
        )
        ret["choices"] = [
            (
                choice[0],
                bleach.clean(
                    choice[1], tags=ALLOWED_TAGS, styles=[], strip=True
                ),
                instance.is_correct(i),
            )
            for (i, choice) in enumerate(ret["choices"], 1)
        ]
        return ret


class RankSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)

    class Meta:
        model = AssignmentQuestions
        fields = ["question", "rank", "pk"]


class AssignmentSerializer(serializers.ModelSerializer):
    questions = RankSerializer(source="assignmentquestions_set", many=True)

    def update(self, instance, validated_data):
        for i, aq in enumerate(instance.assignmentquestions_set.all()):
            aq.rank = validated_data["assignmentquestions_set"][i]["rank"]
            aq.save()
        return instance

    class Meta:
        model = Assignment
        fields = ["title", "questions"]
