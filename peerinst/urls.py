# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Backport of django 1.9 password validation
import password_validation.views as password_views
from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.cache import cache_page

# testing
from django.views.decorators.clickjacking import xframe_options_sameorigin

from . import admin_views, views
from .forms import NonStudentPasswordResetForm
from .mixins import student_check


def not_authenticated(user):
    return not user.is_authenticated


def old_patterns():
    return [
        # DALITE
        # Assignment table of contents - Enforce sameorigin to prevent access from LMS  # noqa
        url(
            r"^browse/$",
            xframe_options_sameorigin(views.browse_database),
            name="browse-database",
        ),
        url(
            r"^assignment-list/$",
            xframe_options_sameorigin(views.AssignmentListView.as_view()),
            name="assignment-list",
        ),
        url(
            r"^question/create$",
            views.QuestionCreateView.as_view(),
            name="question-create",
        ),
        url(
            r"^question/clone/(?P<pk>[0-9]+)$",
            views.QuestionCloneView.as_view(),
            name="question-clone",
        ),
        url(
            r"^question/update/(?P<pk>[0-9]+)$",
            views.QuestionUpdateView.as_view(),
            name="question-update",
        ),
        url(
            r"^question/delete", views.question_delete, name="question-delete"
        ),
        url(
            r"^discipline/create$",
            views.DisciplineCreateView.as_view(),
            name="discipline-create",
        ),
        url(
            r"^discipline/form/(?P<pk>[0-9]+)$",
            views.discipline_select_form,
            name="discipline-form",
        ),
        url(
            r"^discipline/form$",
            views.discipline_select_form,
            name="discipline-form",
        ),
        url(
            r"^disciplines/form/(?P<pk>[0-9]+)$",
            views.disciplines_select_form,
            name="disciplines-form",
        ),
        url(
            r"^disciplines/form$",
            views.disciplines_select_form,
            name="disciplines-form",
        ),
        url(
            r"^category/create$",
            views.CategoryCreateView.as_view(),
            name="category-create",
        ),
        url(
            r"^category/form/(?P<pk>[0-9]+)$",
            views.category_select_form,
            name="category-form",
        ),
        url(
            r"^category/form$",
            views.category_select_form,
            name="category-form",
        ),
        url(
            r"^answer-choice/form/(?P<question_id>[0-9]+)$",
            views.answer_choice_form,
            name="answer-choice-form",
        ),
        url(
            r"^sample-answer/form/(?P<question_id>[0-9]+)$",
            admin_views.QuestionPreviewViewBase.as_view(),
            name="sample-answer-form",
        ),
        url(
            r"^sample-answer/form/(?P<question_id>[0-9]+)/done$",
            views.sample_answer_form_done,
            name="sample-answer-form-done",
        ),
        url(
            r"^assignment/copy/(?P<assignment_id>[^/]+)$",
            views.AssignmentCopyView.as_view(),
            name="assignment-copy",
        ),
        url(
            r"^assignment/edit$",
            views.update_assignment_question_list,
            name="assignment-edit-ajax",
        ),
        url(
            r"^assignment/edit/(?P<assignment_id>[^/]+)$",
            views.AssignmentEditView.as_view(),
            name="assignment-edit",
        ),
        url(
            r"^question-search/$",
            views.question_search,
            name="question-search",
        ),
        url(r"^heartbeat/$", views.HeartBeatUrl.as_view(), name="heartbeat"),
        url(
            r"^collection/create$",
            views.CollectionCreateView.as_view(),
            name="collection-create",
        ),
        # Standalone
        url(
            r"^live/access/(?P<token>[0-9A-Za-z=_-]+)/(?P<assignment_hash>[0-9A-Za-z=_-]+)$",  # noqa
            views.live,
            name="live",
        ),
        url(
            r"^live/navigate/(?P<assignment_id>[^/]+)/(?P<question_id>\d+)/(?P<direction>(next|prev|goto))/(?P<index>[0-9x]+)$",  # noqa
            views.navigate_assignment,
            name="navigate-assignment",
        ),
        url(
            r"^live/signup/form/(?P<group_hash>[0-9A-Za-z=_-]+)$",
            views.signup_through_link,
            name="signup-through-link",
        ),
        url(
            r"^live/studentgroupassignment/create/(?P<assignment_id>[^/]+)$",
            views.StudentGroupAssignmentCreateView.as_view(),
            name="student-group-assignment-create",
        ),
        # Admin
        url(r"^dashboard/$", views.dashboard, name="dashboard"),
        url(
            r"^admin/$",
            admin_views.AdminIndexView.as_view(),
            name="admin-index",
        ),
        url(
            r"^admin/peerinst/",
            include(
                [
                    url(
                        r"^assignment_results/(?P<assignment_id>[^/]+)/",
                        include(
                            [
                                url(
                                    r"^$",
                                    admin_views.AssignmentResultsView.as_view(),  # noqa
                                    name="assignment-results",
                                ),
                                url(
                                    r"^rationales/(?P<question_id>\d+)$",
                                    admin_views.QuestionRationaleView.as_view(),  # noqa
                                    name="question-rationales",
                                ),
                            ]
                        ),
                    ),
                    url(
                        r"^question_preview/(?P<question_id>[^/]+)$",
                        admin_views.QuestionPreviewView.as_view(),
                        name="question-preview",
                    ),
                    url(
                        r"^fake_usernames/$",
                        admin_views.FakeUsernames.as_view(),
                        name="fake-usernames",
                    ),
                    url(
                        r"^fake_countries/$",
                        admin_views.FakeCountries.as_view(),
                        name="fake-countries",
                    ),
                    url(
                        r"^attribution_analysis/$",
                        admin_views.AttributionAnalysis.as_view(),
                        name="attribution-analysis",
                    ),
                    url(
                        r"^group_assignment_management/$",
                        admin_views.StudentGroupAssignmentManagement.as_view(),
                        name="group-assignment-management",
                    ),
                ]
            ),
        ),
        # Teachers
        url(
            r"^teacher-account/(?P<pk>[0-9]+)/$",
            views.TeacherDetailView.as_view(),
            name="teacher",
        ),
        url(
            r"^teacher/(?P<pk>[0-9]+)/$",
            views.TeacherUpdate.as_view(),
            name="teacher-update",
        ),
        url(
            r"^teacher/(?P<pk>[0-9]+)/assignments/$",
            views.TeacherAssignments.as_view(),
            name="teacher-assignments",
        ),
        url(
            r"^teacher/(?P<pk>[0-9]+)/blinks/$",
            views.TeacherBlinks.as_view(),
            name="teacher-blinks",
        ),
        url(
            r"^teacher/favourite",
            views.teacher_toggle_favourite,
            name="teacher-toggle-favourite",
        ),
        url(
            r"^teacher/(?P<pk>[0-9]+)/groups/$",
            views.TeacherGroups.as_view(),
            name="teacher-groups",
        ),
        url(
            r"^teacher/(?P<pk>[0-9]+)/group/(?P<group_hash>[0-9A-Za-z=_-]+)/share$",  # noqa
            views.TeacherGroupShare.as_view(),
            name="group-share",
        ),
        url(
            r"^teacher/(?P<teacher_id>[0-9]+)/group_assignments/$",
            views.StudentGroupAssignmentListView.as_view(),
            name="group-assignments",
        ),
        url(
            r"^teacher/student_activity/$",
            views.student_activity,
            name="student-activity",
        ),
        url(
            r"^teacher/report/all_groups/(?P<assignment_id>[^/]+)/$",
            views.report,
            name="report-all-groups",
        ),
        url(
            r"^teacher/report/all_assignments/(?P<group_id>[^/]+)/$",
            views.report,
            name="report-all-assignments",
        ),
        url(
            r"^teacher/report_selector$",
            views.report_selector,
            name="report_selector",
        ),
        url(r"^teacher/custom_report/$", views.report, name="report-custom"),
        url(
            r"^report_rationales_chosen$",
            views.report_assignment_aggregates,
            name="report_rationales_chosen",
        ),
        # Auth
        url(r"^$", views.landing_page, name="landing_page"),
        url(r"^signup/$", views.sign_up, name="sign_up"),
        url(
            r"^login/$",
            user_passes_test(not_authenticated, login_url="/welcome/")(
                auth_views.login
            ),
            name="login",
        ),
        url(r"^logout/$", views.logout_view, name="logout"),
        url(r"^welcome/$", views.welcome, name="welcome"),
        # Only non-students can change their password
        url(
            r"^password_change/$",
            user_passes_test(student_check)(password_views.password_change),
            name="password_change",
        ),
        url(
            r"^password_change/done/$",
            auth_views.password_change_done,
            name="password_change_done",
        ),
        url(
            r"^password_reset/$",
            auth_views.password_reset,
            {
                "html_email_template_name": "registration/password_reset_email_html.html",  # noqa
                "password_reset_form": NonStudentPasswordResetForm,
            },
            name="password_reset",
        ),
        url(
            r"^password_reset/done/$",
            auth_views.password_reset_done,
            name="password_reset_done",
        ),
        url(
            r"^reset/(?P<uidb64>[0-9A-Za-z_\-=]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",  # noqa
            password_views.password_reset_confirm,
            name="password_reset_confirm",
        ),
        url(
            r"^reset/done/$",
            auth_views.password_reset_complete,
            name="password_reset_complete",
        ),
        url(
            r"^terms_of_service/teachers/$",
            views.terms_teacher,
            name="terms_teacher",
        ),
        url(r"^access_denied/$", views.access_denied, name="access_denied"),
        url(
            r"^access_denied_and_logout/$",
            views.access_denied_and_logout,
            name="access_denied_and_logout",
        ),
        # Blink
        url(
            r"^blink/(?P<pk>[0-9]+)/$",
            views.BlinkQuestionFormView.as_view(),
            name="blink-question",
        ),
        url(
            r"^blink/(?P<pk>[0-9]+)/summary/$",
            views.BlinkQuestionDetailView.as_view(),
            name="blink-summary",
        ),
        url(
            r"^blink/(?P<pk>[0-9]+)/count/$",
            views.blink_count,
            name="blink-count",
        ),
        url(
            r"^blink/(?P<pk>[0-9]+)/close/$",
            views.blink_close,
            name="blink-close",
        ),
        url(
            r"^blink/(?P<pk>[0-9]+)/latest_results/$",
            views.blink_latest_results,
            name="blink-results",
        ),
        url(
            r"^blink/(?P<pk>[0-9]+)/reset/$",
            views.blink_reset,
            name="blink-reset",
        ),
        url(
            r"^blink/(?P<pk>[0-9]+)/status/$",
            views.blink_status,
            name="blink-status",
        ),
        url(
            r"^blink/(?P<username>[\w.@+-]+)/$",
            views.blink_get_current,
            name="blink-get-current",
        ),
        url(
            r"^blink/(?P<username>[\w.@+-]+)/url/$",
            cache_page(1)(views.blink_get_current_url),
            name="blink-get-current-url",
        ),
        url(
            r"^blink/(?P<pk>[0-9]+)/get_next/$",
            views.blink_get_next,
            name="blink-get-next",
        ),
        url(
            r"^blink/waiting/(?P<username>[\w.@+-]+)/$",
            views.blink_waiting,
            name="blink-waiting",
        ),
        url(
            r"^blink/waiting/(?P<username>[\w.@+-]+)/(?P<assignment>[0-9]+)/$",
            views.blink_waiting,
            name="blink-waiting",
        ),
        url(
            r"^blinkAssignment/create/$",
            views.BlinkAssignmentCreate.as_view(),
            name="blinkAssignment-create",
        ),
        url(
            r"^blinkAssignment/(?P<pk>[0-9]+)/delete/$",
            views.blink_assignment_delete,
            name="blinkAssignment-delete",
        ),
        url(
            r"^blinkAssignment/(?P<pk>[0-9]+)/set_time/$",
            views.blink_assignment_set_time,
            name="blinkAssignment-set-time",
        ),
        url(
            r"^blinkAssignment/(?P<pk>[0-9]+)/start/$",
            views.blink_assignment_start,
            name="blinkAssignment-start",
        ),
        url(
            r"^blinkAssignment/(?P<pk>[0-9]+)/update/$",
            views.BlinkAssignmentUpdate.as_view(),
            name="blinkAssignment-update",
        ),
    ]


def group_patterns():
    return [
        url(
            r"^group/(?P<group_hash>[0-9A-Za-z=_-]+)/$",
            views.group_details_page,
            name="group-details",
        ),
        url(
            r"^group/(?P<group_hash>[0-9A-Za-z=_-]+)/update/$",
            views.group_details_update,
            name="group-details-update",
        ),
        url(
            r"^group-assignment/(?P<assignment_hash>[0-9A-Za-z=_-]+)/$",
            views.group_assignment_page,
            name="group-assignment",
        ),
        url(
            r"^group-assignment/(?P<assignment_hash>[0-9A-Za-z=_-]+)/remove/$",
            views.group_assignment_remove,
            name="group-assignment-remove",
        ),
        url(
            r"^group-assignment/(?P<assignment_hash>[0-9A-Za-z=_-]+)/update/$",
            views.group_assignment_update,
            name="group-assignment-update",
        ),
        url(
            r"^group-assignment/(?P<assignment_hash>[0-9A-Za-z=_-]+)/send/$",
            views.send_student_assignment,
            name="send-student-assignment",
        ),
        url(
            r"^group-assignment/(?P<assignment_hash>[0-9A-Za-z=_-]+)/student-progress/$",  # noqa
            views.get_assignment_student_progress,
            name="get-assignment-student-progress",
        ),
        url(
            r"^group-assignment/(?P<assignment_hash>[0-9A-Za-z=_-]+)/"
            r"distribute/$",
            views.distribute_assignment,
            name="distribute-assignment",
        ),
    ]


def student_patterns():
    return [
        url(
            r"^assignment-complete/$",
            views.finish_assignment,
            name="finish-assignment",
        ),
        url(r"^student/$", views.student.index_page, name="student-page"),
        url(
            r"^student/join-group/$",
            views.student.join_group,
            name="student-join-group",
        ),
        url(
            r"^student/leave-group/$",
            views.student.leave_group,
            name="student-leave-group",
        ),
        url(
            r"^student/toggle-group-notifications/$",
            views.student.toggle_group_notifications,
            name="student-toggle-group-notifications",
        ),
        url(
            r"^student/login/$", views.student.login_page, name="student-login"
        ),
        url(
            r"^student/login-confirm/$",
            views.student.send_signin_link,
            name="student-send-signin-link",
        ),
        url(
            r"^student/remove-notification/$",
            views.student.remove_notification,
            name="student-remove-notification",
        ),
        url(
            r"^student/remove-notifications/$",
            views.student.remove_notifications,
            name="student-remove-notifications",
        ),
        url(
            r"^student/get-notifications/$",
            views.student.get_notifications,
            name="student-get-notifications",
        ),
        url(
            r"^student/update/student-id/$",
            views.student.update_student_id,
            name="student-change-id",
        ),
    ]


def search_patterns():
    return [
        url(r"^search/user$", views.search_users, name="search-users"),
        url(
            r"^search/category$",
            views.search_categories,
            name="search-categories",
        ),
    ]


def researcher_patterns():
    return [
        url(r"^research/$", views.research_index, name="research-index"),
        url(
            r"^research/discipline/(?P<discipline_title>[^/]+)$",
            views.research_discipline_question_index,
            name="research-discipline-question-index-by-discipline",
        ),
        url(
            r"^research/assignment/(?P<assignment_id>[^/]+)$",
            views.research_discipline_question_index,
            name="research-assignment-question-index-by-assignment",
        ),
        url(
            r"^research/all_scores/discipline/(?P<discipline_title>[^/]+)/(?P<question_pk>[^/]+)$",  # noqa
            views.research_all_annotations_for_question,
            name="research-all-annotations-for-question-by-discipline",
        ),
        url(
            r"^research/all_scores/assignment/(?P<assignment_id>[^/]+)/(?P<question_pk>[^/]+)$",  # noqa
            views.research_all_annotations_for_question,
            name="research-all-annotations-for-question-by-assignment",
        ),
        url(
            r"^research/discipline/(?P<discipline_title>[^/]+)/(?P<question_pk>[^/]+)/(?P<answerchoice_value>[^/]+)$",  # noqa
            views.research_question_answer_list,
            name="research-question-answer-list-by-discipline",
        ),
        url(
            r"^research/assignment/(?P<assignment_id>[^/]+)/(?P<question_pk>[^/]+)/(?P<answerchoice_value>[^/]+)$",  # noqa
            views.research_question_answer_list,
            name="research-question-answer-list-by-assignment",
        ),
        url(
            r"^research/question/flag/discipline/(?P<discipline_title>[^/]+)/(?P<question_pk>[^/]+)$",  # noqa
            views.flag_question_form,
            name="research-flag-question-by-discipline",
        ),
        url(
            r"^research/question/flag/assignment/(?P<assignment_id>[^/]+)/(?P<question_pk>[^/]+)$",  # noqa
            views.flag_question_form,
            name="research-flag-question-by-assignment",
        ),
        url(
            r"^expert/rationales/(?P<question_id>[0-9]+)$",
            admin_views.QuestionExpertRationaleView.as_view(),
            name="research-fix-expert-rationale",
        ),
        url(
            r"^research/assignment/(?P<assignment_id>[^/]+)/expert/rationale/(?P<question_id>[0-9]+)$",  # noqa
            admin_views.QuestionExpertRationaleView.as_view(),
            name="research-fix-expert-rationale",
        ),
        url(
            r"^research/expert/rationale/fix/(?P<pk>[0-9]+)$",
            views.AnswerExpertUpdateView.as_view(),
            name="research-rationale-update-expert",
        ),
    ]


def collection_patterns():
    return []


def teacher_patterns():
    return [
        url(
            r"^teacher/page/$", views.teacher.teacher_page, name="teacher-page"
        ),
        url(
            r"^teacher/page/new-questions/$",
            views.teacher.new_questions,
            name="teacher-page--new-questions",
        ),
        url(
            r"^teacher/page/student-activity/$",
            views.teacher.student_activity,
            name="teacher-page--student-activity",
        ),
        url(
            r"^teacher/page/rationales/evaluate$",
            views.teacher.evaluate_rationale,
            name="teacher-page--evaluate-rationale",
        ),
        url(
            r"^teacher/page/rationales/$",
            views.teacher.rationales_to_score,
            name="teacher-page--rationales",
        ),
        url(
            r"^teacher/page/collections/$",
            views.teacher.collections,
            name="teacher-page--collections",
        ),
        url(
            r"^teacher/page/messages/$",
            views.teacher.messages,
            name="teacher-page--messages",
        ),
        url(
            r"^teacher/page/unsubscribe-thread/$",
            views.teacher.unsubscribe_from_thread,
            name="teacher-page--unsubscribe-thread",
        ),
        url(
            r"^teacher/gradebook/request/$",
            views.teacher.request_gradebook,
            name="teacher-gradebook--request",
        ),
        url(
            r"^teacher/gradebook/result/$",
            views.teacher.get_gradebook_task_result,
            name="teacher-gradebook--result",
        ),
        url(
            r"^teacher/gradebook/remove/$",
            views.teacher.remove_gradebook_task,
            name="teacher-gradebook--remove",
        ),
        url(
            r"^teacher/gradebook/download/$",
            views.teacher.download_gradebook,
            name="teacher-gradebook--download",
        ),
        url(
            r"^teacher/tasks/$", views.teacher.get_tasks, name="teacher-tasks"
        ),
    ]


urlpatterns = sum(
    [
        old_patterns(),
        group_patterns(),
        student_patterns(),
        search_patterns(),
        researcher_patterns(),
        collection_patterns(),
        teacher_patterns(),
    ],
    [],
)
