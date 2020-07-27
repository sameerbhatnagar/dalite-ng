from rest_framework import viewsets, generics
from rest_framework.renderers import JSONRenderer

from peerinst.models import (
    Assignment,
    AssignmentQuestions,
    Answer,
    AnswerAnnotation,
    Discipline,
    Teacher,
)
from peerinst.util import question_search_function
from REST.pagination import SearchPagination
from REST.serializers import (
    AssignmentSerializer,
    AnswerSerializer,
    DisciplineSerializer,
    FeedbackWriteSerialzer,
    FeedbackReadSerialzer,
    QuestionSerializer,
    RankSerializer,
    TeacherSerializer,
)
from REST.permissions import (
    InAssignmentOwnerList,
    InOwnerList,
    IsAdminUserOrReadOnly,
)


class AssignmentViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing assignments.
    """

    serializer_class = AssignmentSerializer
    permission_classes = [InOwnerList]

    def get_queryset(self):
        return Assignment.objects.filter(owner=self.request.user)


class DisciplineViewSet(viewsets.ModelViewSet):
    serializer_class = DisciplineSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = Discipline.objects.all()


class QuestionListViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for adding/removing assignment questions.
    """

    serializer_class = RankSerializer
    permission_classes = [InAssignmentOwnerList]

    def get_queryset(self):
        return AssignmentQuestions.objects.filter(
            assignment__owner=self.request.user
        )


class QuestionSearchList(generics.ListAPIView):
    """ A simple ListView to return search results in JSON format"""

    pagination_class = SearchPagination
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        search_string = self.request.GET.get("search_string")
        queryset = question_search_function(search_string, is_old_query=True)
        try:
            assignment = Assignment.objects.get(
                pk=self.request.GET.get("assignment_id")
            )
            queryset = queryset.exclude(pk__in=assignment.questions.all())
        except Exception as e:
            print(e)
        return queryset

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        return QuestionSerializer(
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
            *args,
            **kwargs
        )


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

    serializer_class = FeedbackReadSerialzer

    def get_queryset(self):
        return AnswerAnnotation.objects.filter(
            answer__user_token=self.request.user.username, score__isnull=False
        )


class TeacherView(generics.RetrieveUpdateAPIView):
    serializer_class = TeacherSerializer
    queryset = Teacher.objects.all()
    renderer_classes = [JSONRenderer]


class TeacherFeedbackList(generics.ListCreateAPIView):
    """
    endpoint to list authenticated user's feedback given
    (AnswerAnnotation objects where they are annotator),
    or create new one
    """

    serializer_class = FeedbackWriteSerialzer

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

    serializer_class = FeedbackWriteSerialzer

    def get_queryset(self):
        return AnswerAnnotation.objects.filter(
            annotator=self.request.user, score__isnull=False
        )
