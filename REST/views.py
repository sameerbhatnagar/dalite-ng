from rest_framework import viewsets

from peerinst.models import Assignment
from REST.serializers import AssignmentSerializer


class AssignmentViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """

    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
