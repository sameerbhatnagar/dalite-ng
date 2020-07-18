from rest_framework import viewsets, generics
from rest_framework.views import APIView
from rest_framework.response import Response

from peerinst.models import Assignment, Answer, AnswerAnnotation
from REST.serializers import (
    AssignmentSerializer,
    AnswerSerializer,
    AnswerAnnotationSerialzer,
)


class AssignmentViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """

    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer


class ReviewAnswersListView(generics.ListAPIView):
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


class FeedbackAnswersListView(APIView):
    """
    List all Feedback (AnswerAnnotation objects) for
    authenticated student's answers
    """

    def get(self, request, format=None):
        feedback = AnswerAnnotation.objects.filter(
            answer__user_token=request.user.username, score__isnull=False
        )
        serializer = AnswerAnnotationSerialzer(feedback, many=True)
        return Response(serializer.data)
