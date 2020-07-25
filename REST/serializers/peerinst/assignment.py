import bleach

from django.contrib.auth.models import User
from django.template.defaultfilters import title
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from peerinst.models import (
    Assignment,
    AssignmentQuestions,
    Category,
    Discipline,
    Question,
)
from peerinst.templatetags.bleach_html import ALLOWED_TAGS

from .dynamic_serializer import DynamicFieldsModelSerializer


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
        fields = ["title", "pk"]

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


class QuestionSerializer(DynamicFieldsModelSerializer):
    answer_count = serializers.SerializerMethodField()
    category = CategorySerializer(many=True, read_only=True)
    choices = serializers.SerializerMethodField()
    discipline = DisciplineSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    most_convincing_rationales = serializers.SerializerMethodField()
    matrix = serializers.SerializerMethodField()
    collaborators = UserSerializer(many=True, read_only=True)

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
            "collaborators",
        ]

    def to_representation(self, instance):
        """Bleach HTML-supported fields"""
        ret = super().to_representation(instance)
        if "title" in ret:
            ret["title"] = bleach.clean(
                ret["title"], tags=ALLOWED_TAGS, styles=[], strip=True
            )
        if "text" in ret:
            ret["text"] = bleach.clean(
                ret["text"], tags=ALLOWED_TAGS, styles=[], strip=True
            )
        if "choices" in ret:
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
    question = QuestionSerializer(
        read_only=True,
        fields=(
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
            "matrix",
            "collaborators",
        ),
    )

    def create(self, validated_data):
        """ Custom create method to add questions to an assignment based on pk
            Required POST data:
                - assignment (validated normally)
                - question_pk (validated here)
        """

        if "question_pk" in self.context["request"].data:
            try:
                question_pk = self.context["request"].data["question_pk"]
                added_question = AssignmentQuestions.objects.create(
                    assignment=validated_data["assignment"],
                    question=Question.objects.get(pk=question_pk),
                    rank=validated_data["assignment"].questions.count(),
                )
                if added_question:
                    return added_question
                else:
                    raise Exception
            except Exception as e:
                raise ValidationError(e)
        else:
            raise ValidationError("Missing question_pk")

    class Meta:
        model = AssignmentQuestions
        fields = ["assignment", "question", "rank", "pk"]


class AssignmentSerializer(serializers.ModelSerializer):
    questions = RankSerializer(source="assignmentquestions_set", many=True)

    def update(self, instance, validated_data):
        for i, aq in enumerate(instance.assignmentquestions_set.all()):
            aq.rank = validated_data["assignmentquestions_set"][i]["rank"]
            aq.save()
        return instance

    def to_representation(self, instance):
        """Bleach HTML-supported fields"""
        ret = super().to_representation(instance)
        if "title" in ret:
            ret["title"] = bleach.clean(
                ret["title"], tags=ALLOWED_TAGS, styles=[], strip=True
            )
        return ret

    class Meta:
        model = Assignment
        fields = ["title", "questions"]
