import bleach

from rest_framework import serializers

from peerinst.models import (
    Answer,
    AnswerAnnotation,
    AnswerChoice,
    ShownRationale,
)

from .assignment import QuestionSerializer

from peerinst.templatetags.bleach_html import ALLOWED_TAGS


class AnswerSerializer(serializers.ModelSerializer):
    answer_choice = serializers.SerializerMethodField()
    vote_count = serializers.SerializerMethodField()
    shown_count = serializers.SerializerMethodField()
    teacher_feedback = serializers.SerializerMethodField()
    question = QuestionSerializer(read_only=True)

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

    def get_teacher_feedback(self, obj):
        return AnswerAnnotation.objects.filter(
            answer=obj, score__isnull=False
        ).values("score", "annotator__username", "note")

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["rationale"] = bleach.clean(
            ret["rationale"], tags=ALLOWED_TAGS, styles=[], strip=True
        )
        return ret

    class Meta:
        model = Answer
        fields = [
            "answer_choice",
            "rationale",
            "vote_count",
            "shown_count",
            "teacher_feedback",
            "question",
        ]
        ordering = ["-vote_count"]
