# Backport of django 1.9 password validation
import password_validation.views as password_views
from django.conf.urls import include
from django.urls import re_path
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
        re_path(
            r"^browse/$",
            xframe_options_sameorigin(views.browse_database),
            name="browse-database",
        ),
        re_path(
            r"^assignment-list/$",
            xframe_options_sameorigin(views.AssignmentListView.as_view()),
            name="assignment-list",
        ),
        re_path(
            r"^question/create$",
            views.QuestionCreateView.as_view(),
            name="question-create",
        ),
        re_path(
            r"^question/clone/<int:pk>$",
            views.QuestionCloneView.as_view(),
            name="question-clone",
        ),
        re_path(
            r"^question/update/<int:pk>$",
            views.QuestionUpdateView.as_view(),
            name="question-update",
        ),
        re_path(
            r"^question/delete", views.question_delete, name="question-delete"
        ),
        re_path(
            r"^discipline/create$",
            views.DisciplineCreateView.as_view(),
            name="discipline-create",
        ),
        re_path(
            r"^discipline/form/<int:pk>$",
            views.discipline_select_form,
            name="discipline-form",
        ),
        re_path(
            r"^discipline/form$",
            views.discipline_select_form,
            name="discipline-form",
        ),
        re_path(
            r"^disciplines/form/<int:pk>$",
            views.disciplines_select_form,
            name="disciplines-form",
        ),
        re_path(
            r"^disciplines/form$",
            views.disciplines_select_form,
            name="disciplines-form",
        ),
        re_path(
            r"^category/create$",
            views.CategoryCreateView.as_view(),
            name="category-create",
        ),
        re_path(
            r"^category/form/<int:pk>$",
            views.category_select_form,
            name="category-form",
        ),
        re_path(
            r"^category/form$",
            views.category_select_form,
            name="category-form",
        ),
        re_path(
            r"^answer-choice/form/<int:question_id>$",
            views.answer_choice_form,
            name="answer-choice-form",
        ),
        re_path(
            r"^sample-answer/form/<int:question_id>$",
            admin_views.QuestionPreviewViewBase.as_view(),
            name="sample-answer-form",
        ),
        re_path(
            r"^sample-answer/form/<int:question_id>/done$",
            views.sample_answer_form_done,
            name="sample-answer-form-done",
        ),
        re_path(
            r"^assignment/copy/<int:assignment_id>$",
            views.AssignmentCopyView.as_view(),
            name="assignment-copy",
        ),
        re_path(
            r"^assignment/edit$",
            views.update_assignment_question_list,
            name="assignment-edit-ajax",
        ),
        re_path(
            r"^assignment/edit/<int:assignment_id>$",
            views.AssignmentEditView.as_view(),
            name="assignment-edit",
        ),
        re_path(
            r"^question-search/$",
            views.question_search,
            name="question-search",
        ),
        # Standalone
        re_path(
            r"^live/access/(?P<token>[0-9A-Za-z=_-]+)/<assignment_hash>$",  # noqa
            views.live,
            name="live",
        ),
        re_path(
            r"^live/navigate/<int:assignment_id>/(?P<question_id>\d+)/(?P<direction>(next|prev|goto))/(?P<index>[0-9x]+)$",  # noqa
            views.navigate_assignment,
            name="navigate-assignment",
        ),
        re_path(
            r"^live/signup/form/<group_hash>$",
            views.signup_through_link,
            name="signup-through-link",
        ),
        re_path(
            r"^live/studentgroupassignment/create/<int:assignment_id>$",
            views.StudentGroupAssignmentCreateView.as_view(),
            name="student-group-assignment-create",
        ),
        # Admin
        re_path(r"^dashboard/$", views.dashboard, name="dashboard"),
        re_path(
            r"^admin/$",
            admin_views.AdminIndexView.as_view(),
            name="admin-index",
        ),
        re_path(
            r"^admin/peerinst/",
            include(
                [
                    re_path(
                        r"^assignment_results/<int:assignment_id>/",
                        include(
                            [
                                re_path(
                                    r"^$",
                                    admin_views.AssignmentResultsView.as_view(),  # noqa
                                    name="assignment-results",
                                ),
                                re_path(
                                    r"^rationales/(?P<question_id>\d+)$",
                                    admin_views.QuestionRationaleView.as_view(),  # noqa
                                    name="question-rationales",
                                ),
                            ]
                        ),
                    ),
                    re_path(
                        r"^question_preview/<int:question_id>$",
                        admin_views.QuestionPreviewView.as_view(),
                        name="question-preview",
                    ),
                    re_path(
                        r"^fake_usernames/$",
                        admin_views.FakeUsernames.as_view(),
                        name="fake-usernames",
                    ),
                    re_path(
                        r"^fake_countries/$",
                        admin_views.FakeCountries.as_view(),
                        name="fake-countries",
                    ),
                    re_path(
                        r"^attribution_analysis/$",
                        admin_views.AttributionAnalysis.as_view(),
                        name="attribution-analysis",
                    ),
                    re_path(
                        r"^group_assignment_management/$",
                        admin_views.StudentGroupAssignmentManagement.as_view(),
                        name="group-assignment-management",
                    ),
                ]
            ),
        ),
        # Teachers
        re_path(
            r"^teacher-account/<int:pk>/$",
            views.TeacherDetailView.as_view(),
            name="teacher",
        ),
        re_path(
            r"^teacher/<int:pk>/$",
            views.TeacherUpdate.as_view(),
            name="teacher-update",
        ),
        re_path(
            r"^teacher/<int:pk>/assignments/$",
            views.TeacherAssignments.as_view(),
            name="teacher-assignments",
        ),
        re_path(
            r"^teacher/<int:pk>/blinks/$",
            views.TeacherBlinks.as_view(),
            name="teacher-blinks",
        ),
        re_path(
            r"^teacher/favourite",
            views.teacher_toggle_favourite,
            name="teacher-toggle-favourite",
        ),
        re_path(
            r"^teacher/<int:pk>/groups/$",
            views.TeacherGroups.as_view(),
            name="teacher-groups",
        ),
        re_path(
            r"^teacher/<int:pk>/group/<group_hash>/share$",  # noqa
            views.TeacherGroupShare.as_view(),
            name="group-share",
        ),
        re_path(
            r"^teacher/(?P<teacher_id>[0-9]+)/group_assignments/$",
            views.StudentGroupAssignmentListView.as_view(),
            name="group-assignments",
        ),
        re_path(
            r"^teacher/student_activity/$",
            views.student_activity,
            name="student-activity",
        ),
        re_path(
            r"^teacher/report/all_groups/<int:assignment_id>/$",
            views.report,
            name="report-all-groups",
        ),
        re_path(
            r"^teacher/report/all_assignments/(?P<group_id>[^/]+)/$",
            views.report,
            name="report-all-assignments",
        ),
        re_path(
            r"^teacher/report_selector$",
            views.report_selector,
            name="report_selector",
        ),
        re_path(
            r"^teacher/custom_report/$", views.report, name="report-custom"
        ),
        re_path(
            r"^report_rationales_chosen$",
            views.report_assignment_aggregates,
            name="report_rationales_chosen",
        ),
        # Auth
        re_path(r"^$", views.landing_page, name="landing_page"),
        re_path(r"^signup/$", views.sign_up, name="sign_up"),
        re_path(
            r"^login/$",
            user_passes_test(not_authenticated, login_url="/welcome/")(
                auth_views.LoginView.as_view()
            ),
            name="login",
        ),
        re_path(r"^logout/$", views.logout_view, name="logout"),
        re_path(r"^welcome/$", views.welcome, name="welcome"),
        # Only non-students can change their password
        re_path(
            r"^password_change/$",
            user_passes_test(student_check)(password_views.password_change),
            name="password_change",
        ),
        re_path(
            r"^password_change/done/$",
            auth_views.PasswordChangeDoneView.as_view(),
            name="password_change_done",
        ),
        re_path(
            r"^password_reset/$",
            auth_views.PasswordResetView.as_view(),
            {
                "html_email_template_name": "registration/password_reset_email_html.html",  # noqa
                "password_reset_form": NonStudentPasswordResetForm,
            },
            name="password_reset",
        ),
        re_path(
            r"^password_reset/done/$",
            auth_views.PasswordResetDoneView.as_view(),
            name="password_reset_done",
        ),
        re_path(
            r"^reset/(?P<uidb64>[0-9A-Za-z_\-=]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",  # noqa
            password_views.password_reset_confirm,
            name="password_reset_confirm",
        ),
        re_path(
            r"^reset/done/$",
            auth_views.PasswordResetCompleteView.as_view(),
            name="password_reset_complete",
        ),
        re_path(
            r"^terms_of_service/teachers/$",
            views.terms_teacher,
            name="terms_teacher",
        ),
        re_path(
            r"^access_denied/$", views.access_denied, name="access_denied"
        ),
        re_path(
            r"^access_denied_and_logout/$",
            views.access_denied_and_logout,
            name="access_denied_and_logout",
        ),
        # Blink
        re_path(
            r"^blink/<int:pk>/$",
            views.BlinkQuestionFormView.as_view(),
            name="blink-question",
        ),
        re_path(
            r"^blink/<int:pk>/summary/$",
            views.BlinkQuestionDetailView.as_view(),
            name="blink-summary",
        ),
        re_path(
            r"^blink/<int:pk>/count/$", views.blink_count, name="blink-count",
        ),
        re_path(
            r"^blink/<int:pk>/close/$", views.blink_close, name="blink-close",
        ),
        re_path(
            r"^blink/<int:pk>/latest_results/$",
            views.blink_latest_results,
            name="blink-results",
        ),
        re_path(
            r"^blink/<int:pk>/reset/$", views.blink_reset, name="blink-reset",
        ),
        re_path(
            r"^blink/<int:pk>/status/$",
            views.blink_status,
            name="blink-status",
        ),
        re_path(
            r"^blink/<username>/$",
            views.blink_get_current,
            name="blink-get-current",
        ),
        re_path(
            r"^blink/<username>/url/$",
            cache_page(1)(views.blink_get_current_url),
            name="blink-get-current-url",
        ),
        re_path(
            r"^blink/<int:pk>/get_next/$",
            views.blink_get_next,
            name="blink-get-next",
        ),
        re_path(
            r"^blink/waiting/(?P<username>[\w.@+-]+)/$",
            views.blink_waiting,
            name="blink-waiting",
        ),
        re_path(
            r"^blink/waiting/<username>/<int:assignment>/$",
            views.blink_waiting,
            name="blink-waiting",
        ),
        re_path(
            r"^blinkAssignment/create/$",
            views.BlinkAssignmentCreate.as_view(),
            name="blinkAssignment-create",
        ),
        re_path(
            r"^blinkAssignment/<int:pk>/delete/$",
            views.blink_assignment_delete,
            name="blinkAssignment-delete",
        ),
        re_path(
            r"^blinkAssignment/<int:pk>/set_time/$",
            views.blink_assignment_set_time,
            name="blinkAssignment-set-time",
        ),
        re_path(
            r"^blinkAssignment/<int:pk>/start/$",
            views.blink_assignment_start,
            name="blinkAssignment-start",
        ),
        re_path(
            r"^blinkAssignment/<int:pk>/update/$",
            views.BlinkAssignmentUpdate.as_view(),
            name="blinkAssignment-update",
        ),
    ]


def group_patterns():
    return [
        re_path(
            r"^group/student-information/$",
            views.group.get_student_reputation,
            name="group-details--student-information",
        ),
        re_path(
            r"^group/<group_hash>/$",
            views.group_details_page,
            name="group-details",
        ),
        re_path(
            r"^group/<group_hash>/update/$",
            views.group_details_update,
            name="group-details-update",
        ),
        re_path(
            r"^group-assignment/<assignment_hash>/$",
            views.group_assignment_page,
            name="group-assignment",
        ),
        re_path(
            r"^group-assignment/<assignment_hash>/remove/$",
            views.group_assignment_remove,
            name="group-assignment-remove",
        ),
        re_path(
            r"^group-assignment/<assignment_hash>/update/$",
            views.group_assignment_update,
            name="group-assignment-update",
        ),
        re_path(
            r"^group-assignment/<assignment_hash>/send/$",
            views.send_student_assignment,
            name="send-student-assignment",
        ),
        re_path(
            r"^group-assignment/<assignment_hash>/student-progress/$",  # noqa
            views.get_assignment_student_progress,
            name="get-assignment-student-progress",
        ),
        re_path(
            r"^group-assignment/<assignment_hash>/" r"distribute/$",
            views.distribute_assignment,
            name="distribute-assignment",
        ),
    ]


def student_patterns():
    return [
        re_path(
            r"^assignment-complete/$",
            views.finish_assignment,
            name="finish-assignment",
        ),
        re_path(r"^student/$", views.student.index_page, name="student-page"),
        re_path(
            r"^student/join-group/$",
            views.student.join_group,
            name="student-join-group",
        ),
        re_path(
            r"^student/leave-group/$",
            views.student.leave_group,
            name="student-leave-group",
        ),
        re_path(
            r"^student/toggle-group-notifications/$",
            views.student.toggle_group_notifications,
            name="student-toggle-group-notifications",
        ),
        re_path(
            r"^student/login/$", views.student.login_page, name="student-login"
        ),
        re_path(
            r"^student/login-confirm/$",
            views.student.send_signin_link,
            name="student-send-signin-link",
        ),
        re_path(
            r"^student/remove-notification/$",
            views.student.remove_notification,
            name="student-remove-notification",
        ),
        re_path(
            r"^student/remove-notifications/$",
            views.student.remove_notifications,
            name="student-remove-notifications",
        ),
        re_path(
            r"^student/get-notifications/$",
            views.student.get_notifications,
            name="student-get-notifications",
        ),
        re_path(
            r"^student/update/student-id/$",
            views.student.update_student_id,
            name="student-change-id",
        ),
    ]


def search_patterns():
    return [
        re_path(r"^search/user$", views.search_users, name="search-users"),
        re_path(
            r"^search/category$",
            views.search_categories,
            name="search-categories",
        ),
    ]


def researcher_patterns():
    return [
        re_path(r"^research/$", views.research_index, name="research-index"),
        re_path(
            r"^research/discipline/<discipline_title>$",
            views.research_discipline_question_index,
            name="research-discipline-question-index-by-discipline",
        ),
        re_path(
            r"^research/assignment/<int:assignment_id>$",
            views.research_discipline_question_index,
            name="research-assignment-question-index-by-assignment",
        ),
        re_path(
            r"^research/all_scores/discipline/<discipline_title>/<int:question_pk>$",  # noqa
            views.research_all_annotations_for_question,
            name="research-all-annotations-for-question-by-discipline",
        ),
        re_path(
            r"^research/all_scores/assignment/<int:assignment_id>/<int:question_pk>$",  # noqa
            views.research_all_annotations_for_question,
            name="research-all-annotations-for-question-by-assignment",
        ),
        re_path(
            r"^research/discipline/<discipline_title>/<int:question_pk>/<int:answerchoice_value>$",  # noqa
            views.research_question_answer_list,
            name="research-question-answer-list-by-discipline",
        ),
        re_path(
            r"^research/assignment/<int:assignment_id>/<int:question_pk>/<int:answerchoice_value>$",  # noqa
            views.research_question_answer_list,
            name="research-question-answer-list-by-assignment",
        ),
        re_path(
            r"^research/question/flag/discipline/<discipline_title>/<int:question_pk>$",  # noqa
            views.flag_question_form,
            name="research-flag-question-by-discipline",
        ),
        re_path(
            r"^research/question/flag/assignment/<int:assignment_id>/<int:question_pk>$",  # noqa
            views.flag_question_form,
            name="research-flag-question-by-assignment",
        ),
        re_path(
            r"^expert/rationales/<int:question_id>$",
            admin_views.QuestionExpertRationaleView.as_view(),
            name="research-fix-expert-rationale",
        ),
        re_path(
            r"^research/assignment/<int:assignment_id>/expert/rationale/<int:question_id>$",  # noqa
            admin_views.QuestionExpertRationaleView.as_view(),
            name="research-fix-expert-rationale",
        ),
        re_path(
            r"^research/expert/rationale/fix/<int:pk>$",
            views.AnswerExpertUpdateView.as_view(),
            name="research-rationale-update-expert",
        ),
    ]


def collection_patterns():
    return [
        re_path(
            r"^collection/create/$",
            views.CollectionCreateView.as_view(),
            name="collection-create",
        ),
        re_path(
            r"^collection/<int:pk>$",
            views.CollectionDetailView.as_view(),
            name="collection-detail",
        ),
        re_path(
            r"^collection/update/<int:pk>$",
            views.CollectionUpdateView.as_view(),
            name="collection-update",
        ),
        re_path(
            r"^collection/delete/<int:pk>$",
            views.CollectionDeleteView.as_view(),
            name="collection-delete",
        ),
        re_path(
            r"^collection/list/$",
            views.CollectionListView.as_view(),
            name="collection-list",
        ),
        re_path(
            r"^collection/personal/$",
            views.PersonalCollectionListView.as_view(),
            name="personal-collection-list",
        ),
        re_path(
            r"^collection/followed/$",
            views.FollowedCollectionListView.as_view(),
            name="followed-collection-list",
        ),
        re_path(
            r"^collection/featured/$",
            views.FeaturedCollectionListView.as_view(),
            name="featured-collection-list",
        ),
        re_path(
            r"^collection/distribute/<int:pk>$",
            views.CollectionDistributeDetailView.as_view(),
            name="collection-distribute",
        ),
        re_path(
            r"^collection/follower",
            views.teacher_toggle_follower,
            name="teacher-toggle-follower",
        ),
        re_path(
            r"^collection/assignment",
            views.collection_toggle_assignment,
            name="collection-toggle-assignment",
        ),
        re_path(
            r"^collection/add/assignment",
            views.collection_add_assignment,
            name="collection-add-assignment",
        ),
        re_path(
            r"^collection/assign",
            views.collection_assign,
            name="collection-assign",
        ),
        re_path(
            r"^collection/unassign",
            views.collection_unassign,
            name="collection-unassign",
        ),
        re_path(
            r"^collection/collection-statistics",
            views.collection_statistics,
            name="collection-statistics",
        ),
        re_path(
            r"^collection/featured-data/$",
            views.featured_collections,
            name="collection-featured-data",
        ),
    ]


def teacher_patterns():
    return [
        re_path(
            r"^teacher/dashboard/$",
            views.teacher.dashboard,
            name="teacher-dashboard",
        ),
        re_path(
            r"^teacher/dashboard/new-questions/$",
            views.teacher.new_questions,
            name="teacher-dashboard--new-questions",
        ),
        re_path(
            r"^teacher/dashboard/rationales/evaluate$",
            views.teacher.evaluate_rationale,
            name="teacher-dashboard--evaluate-rationale",
        ),
        re_path(
            r"^teacher/dashboard/rationales/$",
            views.teacher.rationales_to_score,
            name="teacher-dashboard--rationales",
        ),
        re_path(
            r"^teacher/dashboard/collections/$",
            views.teacher.collections,
            name="teacher-dashboard--collections",
        ),
        re_path(
            r"^teacher/dashboard/messages/$",
            views.teacher.messages,
            name="teacher-dashboard--messages",
        ),
        re_path(
            r"^teacher/dashboard/dalite-messages/$",
            views.teacher.dalite_messages,
            name="teacher-dashboard--dalite-messages",
        ),
        re_path(
            r"^teacher/dashboard/dalite-messages/remove$",
            views.teacher.remove_dalite_message,
            name="teacher-dashboard--dalite-messages--remove",
        ),
        re_path(
            r"^teacher/dashboard/messages/read$",
            views.teacher.mark_message_read,
            name="teacher-dashboard--messages--read",
        ),
        re_path(
            r"^teacher/dashboard/unsubscribe-thread/$",
            views.teacher.unsubscribe_from_thread,
            name="teacher-dashboard--unsubscribe-thread",
        ),
        re_path(
            r"^teacher/gradebook/request/$",
            views.teacher.request_gradebook,
            name="teacher-gradebook--request",
        ),
        re_path(
            r"^teacher/gradebook/result/$",
            views.teacher.get_gradebook_task_result,
            name="teacher-gradebook--result",
        ),
        re_path(
            r"^teacher/gradebook/remove/$",
            views.teacher.remove_gradebook_task,
            name="teacher-gradebook--remove",
        ),
        re_path(
            r"^teacher/gradebook/download/$",
            views.teacher.download_gradebook,
            name="teacher-gradebook--download",
        ),
        re_path(
            r"^teacher/tasks/$", views.teacher.get_tasks, name="teacher-tasks"
        ),
    ]


def question_patterns():
    return [
        re_path(
            r"^question/flag/reasons$",
            views.question_.get_flag_question_reasons,
            name="question--flag--reasons",
        ),
        re_path(
            r"^question/flag/flag$",
            views.question_.flag_question,
            name="question--flag--flag",
        ),
    ]


urlpatterns = sum(
    [
        collection_patterns(),
        group_patterns(),
        old_patterns(),
        question_patterns(),
        researcher_patterns(),
        search_patterns(),
        student_patterns(),
        teacher_patterns(),
    ],
    [],
)
