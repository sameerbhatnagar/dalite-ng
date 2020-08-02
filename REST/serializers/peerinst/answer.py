import bleach

from rest_framework import serializers

from peerinst.models import (
    Answer,
    AnswerAnnotation,
    AnswerChoice,
    ShownRationale,
)

from .assignment import QuestionSerializer
from .dynamic_serializer import DynamicFieldsModelSerializer
from peerinst.templatetags.bleach_html import ALLOWED_TAGS


class AnswerSerializer(DynamicFieldsModelSerializer):
    answer_choice = serializers.SerializerMethodField()
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

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["rationale"] = bleach.clean(
            ret["rationale"], tags=ALLOWED_TAGS, styles=[], strip=True
        )
        return ret

    class Meta:
        model = Answer
        fields = [
            "id",
            "answer_choice",
            "rationale",
            "vote_count",
            "shown_count",
            "question",
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
