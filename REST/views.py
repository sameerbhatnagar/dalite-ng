from rest_framework import viewsets, generics

from peerinst.models import (
    Assignment,
    AssignmentQuestions,
    Answer,
    AnswerAnnotation,
)
from REST.serializers import (
    AssignmentSerializer,
    AnswerSerializer,
    AnswerAnnotationSerialzer,
    RankSerializer,
)


class AssignmentViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing assignments.
    """

    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer


class QuestionListViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for editing assignment question.
    """

    queryset = AssignmentQuestions.objects.all()
    serializer_class = RankSerializer


class StudentReviewList(generics.ListAPIView):
    """
    List all answers submitted by authenticated student, with associated
    question and most convincing rationales
    """

    serializer_class = AnswerSerializer

    def get_queryset(self):
        """
        return answers submitted by authenticated student
        """

        student = self.request.user
        return Answer.objects.filter(user_token=student.username)


class StudentFeedbackList(generics.ListAPIView):
    """
    List all Feedback (AnswerAnnotation objects) for
    authenticated student's answers
    """

    serializer_class = AnswerAnnotationSerialzer

    def get_queryset(self):
        return AnswerAnnotation.objects.filter(
            answer__user_token=self.request.user.username, score__isnull=False
        )


class TeacherFeedbackList(generics.ListCreateAPIView):
    """
    endpoint to list authenticated user's feedback given
    (AnswerAnnotation objects where they are annotator),
    or create new one
    """

    serializer_class = AnswerAnnotationSerialzer

    def get_queryset(self):
        return AnswerAnnotation.objects.filter(
            annotator=self.request.user, score__isnull=False
        )

    def perform_create(self, serializer):
        serializer.save(annotator=self.request.user)


class TeacherFeedbackDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    View for RUD operations on AnswerAnnotation model
    """

    serializer_class = AnswerAnnotationSerialzer

    def get_queryset(self):
        return AnswerAnnotation.objects.filter(
            annotator=self.request.user, score__isnull=False
        )
