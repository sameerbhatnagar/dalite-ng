from rest_framework import viewsets, generics

from peerinst.models import Assignment, Answer
from REST.serializers import AssignmentSerializer, AnswerSerializer


class AssignmentViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """

    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer


class StudentAnswerListView(generics.ListAPIView):
    serializer_class = AnswerSerializer

    def get_queryset(self):
        """
        return answers submitted by authenticated student
        """

        student = self.request.user
        return Answer.objects.filter(user_token=student.username)
