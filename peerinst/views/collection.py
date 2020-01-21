from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.views.generic.edit import CreateView
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.forms import ModelForm
from ..models import (
    Assignment,
    Collection,
    StudentGroup,
    StudentGroupAssignment,
    Teacher,
)
from ..mixins import (
    LoginRequiredMixin,
    NoStudentsMixin,
    student_check,
    TOSAcceptanceRequiredMixin,
)
from django.shortcuts import get_object_or_404
from django.urls import reverse
from peerinst.admin_views import get_assignment_aggregates
import collections
from dalite.views.utils import get_json_params
from .decorators import teacher_required
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test


class CollectionForm(ModelForm):
    class Meta:
        model = Collection
        fields = [
            "title",
            "description",
            "image",
            "assignments",
            "discipline",
            "private",
        ]

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop("teacher")
        super(CollectionForm, self).__init__(*args, **kwargs)
        self.fields["assignments"].queryset = teacher.assignments.all()
        self.fields["discipline"].queryset = teacher.disciplines.all()


class CollectionCreateView(
    LoginRequiredMixin, NoStudentsMixin, TOSAcceptanceRequiredMixin, CreateView
):

    template_name = "peerinst/collection/collection_form.html"
    form_class = CollectionForm

    def get_success_url(self):
        return reverse("collection-update", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self):
        kwargs = super(CollectionCreateView, self).get_form_kwargs()
        kwargs["teacher"] = Teacher.objects.get(user=self.request.user)
        return kwargs

    def form_valid(self, form):
        teacher = get_object_or_404(Teacher, user=self.request.user)
        form.instance.owner = teacher
        return super(CollectionCreateView, self).form_valid(form)


class CollectionDetailView(LoginRequiredMixin, NoStudentsMixin, DetailView):
    model = Collection
    template_name = "peerinst/collection/collection_detail.html"

    def dispatch(self, *args, **kwargs):
        teacher = get_object_or_404(Teacher, user=self.request.user)
        if (
            teacher == self.get_object().owner
            or self.get_object().private is False
        ):
            return super(CollectionDetailView, self).dispatch(*args, **kwargs)
        else:
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        collection = self.get_object()
        context["collection_data"] = collection_data(collection=collection)
        context["assignment_data"] = {}
        for assignment in collection.assignments.all():
            context["assignment_data"][assignment.pk] = assignment_data(
                assignment=assignment
            )
        return context


def assignment_data(assignment):
    """
    returns only question sums counter object from assignment aggregates method
    """
    q_sums, q_students = get_assignment_aggregates(assignment=assignment)
    return q_sums


def collection_data(collection):
    """
    sums all of a collection's assignment's counter objects
    """
    assignments = collection.assignments.all()
    a_sums = collections.Counter(
        total_answers=0,
        correct_first_answers=0,
        correct_second_answers=0,
        switches=0,
    )
    for assignment in assignments:
        a_sums += assignment_data(assignment)
    return a_sums


class CollectionUpdateView(LoginRequiredMixin, NoStudentsMixin, UpdateView):
    template_name = "peerinst/collection/collection_update.html"
    model = Collection
    fields = ["title", "description", "image", "discipline", "private"]

    def dispatch(self, *args, **kwargs):
        teacher = get_object_or_404(Teacher, user=self.request.user)
        if teacher == self.get_object().owner or self.request.user.is_staff:
            return super(CollectionUpdateView, self).dispatch(*args, **kwargs)
        else:
            raise PermissionDenied

    def get_success_url(self):
        return reverse("collection-detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context["teacher"] = get_object_or_404(Teacher, user=self.request.user)
        collection = self.get_object()
        teacher = get_object_or_404(Teacher, user=self.request.user)
        context["collection_assignments"] = collection.assignments.all()
        context["owned_assignments"] = [
            a
            for a in list(Assignment.objects.filter(owner=self.request.user))
            if a not in self.get_object().assignments.all()
        ]
        context["followed_assignments"] = [
            a
            for a in teacher.assignments.exclude(owner=self.request.user)
            if a not in self.get_object().assignments.all()
        ]
        return context


class CollectionDeleteView(LoginRequiredMixin, NoStudentsMixin, DeleteView):
    model = Collection
    template_name = "peerinst/collection/collection_delete.html"

    def dispatch(self, *args, **kwargs):
        teacher = get_object_or_404(Teacher, user=self.request.user)
        if teacher == self.get_object().owner or self.request.user.is_staff:
            return super(CollectionDeleteView, self).dispatch(*args, **kwargs)
        else:
            raise PermissionDenied

    def get_success_url(self):
        return reverse("collection-list")


class CollectionListView(LoginRequiredMixin, NoStudentsMixin, ListView):
    """
    list for collections that are public or owned by teacher
    """

    model = Collection
    template_name = "peerinst/collection/collection_list.html"

    def get_queryset(self):
        teacher = get_object_or_404(Teacher, user=self.request.user)
        return Collection.objects.filter(Q(private=False) | Q(owner=teacher))


class PersonalCollectionListView(
    LoginRequiredMixin, NoStudentsMixin, ListView
):
    """
    list for collections where teacher is the owner
    """

    model = Collection
    template_name = "peerinst/collection/personal_collection_list.html"

    def get_queryset(self):
        teacher = get_object_or_404(Teacher, user=self.request.user)
        return Collection.objects.filter(owner=teacher)


class FollowedCollectionListView(
    LoginRequiredMixin, NoStudentsMixin, ListView
):
    """
    list for collections followed by teacher that are public
    or owned by teacher
    """

    model = Collection
    template_name = "peerinst/collection/followed_collection_list.html"

    def get_queryset(self):
        teacher = get_object_or_404(Teacher, user=self.request.user)
        return Collection.objects.filter(
            Q(followers=teacher, private=False)
            | Q(followers=teacher, owner=teacher)
        )


class FeaturedCollectionListView(
    LoginRequiredMixin, NoStudentsMixin, ListView
):
    """
    list for featured collections that are public or owned by teacher
    """

    model = Collection
    template_name = "peerinst/collection/featured_collection_list.html"

    def get_queryset(self):
        teacher = get_object_or_404(Teacher, user=self.request.user)
        return Collection.objects.filter(
            Q(featured=True, private=False) | Q(featured=True, owner=teacher)
        )


def featured_collections(request):
    data = serializers.serialize(
        "json", Collection.objects.filter(featured=True)
    )
    return JsonResponse(data, safe=False)


class CollectionDistributeDetailView(
    LoginRequiredMixin, NoStudentsMixin, DetailView
):
    """
    view to assign/unassign a collection's assignments from a student group
    """

    model = Collection
    template_name = "peerinst/collection/collection_distribute.html"

    def dispatch(self, *args, **kwargs):
        teacher = get_object_or_404(Teacher, user=self.request.user)
        if (
            teacher == self.get_object().owner
            or self.get_object().private is False
        ):
            return super(CollectionDistributeDetailView, self).dispatch(
                *args, **kwargs
            )
        else:
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        teacher = get_object_or_404(Teacher, user=self.request.user)
        collection = self.get_object()
        context["student_groups"] = teacher.current_groups.all()
        context["collection_data"] = collection_data(collection=collection)
        context["group_data"] = {}
        for group in teacher.current_groups.all():
            context["group_data"][group.pk] = True
            for assignment in collection.assignments.all():
                if not StudentGroupAssignment.objects.filter(
                    group=group, assignment=assignment
                ).exists():
                    context["group_data"][group.pk] = False
        return context


@login_required
@user_passes_test(student_check, login_url="/access_denied_and_logout/")
def collection_statistics(request):
    collection = get_object_or_404(Collection, pk=request.POST.get("pk"))
    collection_stats = collection_data(collection=collection)
    data = {
        "totalAnswers": collection_stats["total_answers"],
        "correctFirstAnswers": collection_stats["correct_first_answers"],
        "correctSecondAnswers": collection_stats["correct_second_answers"],
        "switches": collection_stats["switches"],
    }
    return JsonResponse(data)


@teacher_required
@require_POST
def collection_add_assignment(request, teacher):
    """
    creates a collection with assignments from a student group
    used in group detail view
    """
    args = get_json_params(request, args=["group_pk"])
    if isinstance(args, HttpResponse):
        return args
    (group_pk,), _ = args

    collection = Collection.objects.create(
        discipline=teacher.disciplines.first(),
        owner=teacher,
        title="temporary text",
        description="temporary text",
    )
    student_group = get_object_or_404(StudentGroup, pk=group_pk)
    student_group_assignments = student_group.studentgroupassignment_set.all()
    for assignment in student_group_assignments:
        if assignment.assignment not in collection.assignments.all():
            collection.assignments.add(assignment.assignment)
    return JsonResponse({"pk": collection.pk})
