import bleach

from rest_framework import serializers
from django.contrib.auth.models import User

from peerinst.models import (
    Answer,
    AnswerAnnotation,
    AnswerChoice,
    ShownRationale,
    StudentGroupAssignment,
)

from .assignment import QuestionSerializer
from .dynamic_serializer import DynamicFieldsModelSerializer
from peerinst.templatetags.bleach_html import ALLOWED_TAGS


class AnswerSerializer(DynamicFieldsModelSerializer):
    answer_choice = serializers.SerializerMethodField()
    chosen_rationale = serializers.SerializerMethodField()
    vote_count = serializers.SerializerMethodField()
    shown_count = serializers.SerializerMethodField()
    question = QuestionSerializer(
        fields=("title", "text", "image", "choices",), read_only=True
    )

    def get_vote_count(self, obj):
        return Answer.objects.filter(chosen_rationale_id=obj.id).count()

    def get_shown_count(self, obj):
        return ShownRationale.objects.filter(shown_answer=obj).count()

    def get_answer_choice(self, obj):
        if obj.question.type == "RO":
            return None
        else:
            return AnswerChoice.objects.filter(question=obj.question).values(
                "text", "correct"
            )[obj.first_answer_choice - 1]

    def get_chosen_rationale(self, obj):
        if obj.chosen_rationale:
            return obj.chosen_rationale.rationale
        return None

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["rationale"] = bleach.clean(
            ret["rationale"], tags=ALLOWED_TAGS, styles=[], strip=True
        )
        if ret["chosen_rationale"]:
            ret["chosen_rationale"] = bleach.clean(
                ret["chosen_rationale"],
                tags=ALLOWED_TAGS,
                styles=[],
                strip=True,
            )
        return ret

    class Meta:
        model = Answer
        fields = [
            "id",
            "answer_choice",
            "chosen_rationale",
            "first_answer_choice",
            "second_answer_choice",
            "rationale",
            "vote_count",
            "shown_count",
            "question",
            "user_token",
            "datetime_start",
        ]
        read_only_fields = fields
        ordering = ["-vote_count"]


class FeedbackWriteSerialzer(serializers.ModelSerializer):
    annotator = serializers.ReadOnlyField(source="annotator.username")
    answer = serializers.PrimaryKeyRelatedField(queryset=Answer.objects.all())

    class Meta:
        model = AnswerAnnotation
        fields = ["pk", "score", "annotator", "note", "timestamp", "answer"]


class FeedbackReadSerialzer(serializers.ModelSerializer):
    annotator = serializers.ReadOnlyField(source="annotator.username")
    answer = AnswerSerializer(
        fields=("answer_choice", "rationale", "question")
    )

    class Meta:
        model = AnswerAnnotation
        fields = ["score", "annotator", "note", "timestamp", "answer"]


class StudentGroupAssignmentAnswerSerializer(serializers.ModelSerializer):
    """
    A serializer to retrieve answers from a StudentGroupAssignment
    """

    answers = serializers.SerializerMethodField()

    def get_answers(self, obj):
        """
        Field will be a list of all answers for this StudentGroupAssignment for
        a single question
        """

        answers = (
            Answer.objects.filter(
                user_token__in=[
                    student.student.username for student in obj.group.students
                ]
            )
            .filter(assignment=obj.assignment)
            .filter(question__id=self.context["question_pk"])
        )
        answers_serialized = list(
            AnswerSerializer(
                a,
                fields=(
                    "chosen_rationale",
                    "datetime_start",
                    "first_answer_choice",
                    "id",
                    "rationale",
                    "second_answer_choice",
                    "user_token",
                ),
            ).data
            for a in answers
        )
        for a in answers_serialized:
            a.update(
                {
                    "user_email": User.objects.get(
                        username=a["user_token"]
                    ).email.split("@")[0]
                }
            )
        return answers_serialized

    class Meta:
        model = StudentGroupAssignment
        fields = ["pk", "answers"]
