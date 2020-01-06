# Backport of django 1.9 password validation
import password_validation.views as password_views
from django.conf.urls import include, path
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
        path(
            r"^browse/$",
            xframe_options_sameorigin(views.browse_database),
            name="browse-database",
        ),
        path(
            r"^assignment-list/$",
            xframe_options_sameorigin(views.AssignmentListView.as_view()),
            name="assignment-list",
        ),
        path(
            r"^question/create$",
            views.QuestionCreateView.as_view(),
            name="question-create",
        ),
        path(
            r"^question/clone/<int:pk>$",
            views.QuestionCloneView.as_view(),
            name="question-clone",
        ),
        path(
            r"^question/update/<int:pk>$",
            views.QuestionUpdateView.as_view(),
            name="question-update",
        ),
        path(
            r"^question/delete", views.question_delete, name="question-delete"
        ),
        path(
            r"^discipline/create$",
            views.DisciplineCreateView.as_view(),
            name="discipline-create",
        ),
        path(
            r"^discipline/form/<int:pk>$",
            views.discipline_select_form,
            name="discipline-form",
        ),
        path(
            r"^discipline/form$",
            views.discipline_select_form,
            name="discipline-form",
        ),
        path(
            r"^disciplines/form/<int:pk>$",
            views.disciplines_select_form,
            name="disciplines-form",
        ),
        path(
            r"^disciplines/form$",
            views.disciplines_select_form,
            name="disciplines-form",
        ),
        path(
            r"^category/create$",
            views.CategoryCreateView.as_view(),
            name="category-create",
        ),
        path(
            r"^category/form/<int:pk>$",
            views.category_select_form,
            name="category-form",
        ),
        path(
            r"^category/form$",
            views.category_select_form,
            name="category-form",
        ),
        path(
            r"^answer-choice/form/<int:question_id>$",
            views.answer_choice_form,
            name="answer-choice-form",
        ),
        path(
            r"^sample-answer/form/<int:question_id>$",
            admin_views.QuestionPreviewViewBase.as_view(),
            name="sample-answer-form",
        ),
        path(
            r"^sample-answer/form/<int:question_id>/done$",
            views.sample_answer_form_done,
            name="sample-answer-form-done",
        ),
        path(
            r"^assignment/copy/<int:assignment_id>$",
            views.AssignmentCopyView.as_view(),
            name="assignment-copy",
        ),
        path(
            r"^assignment/edit$",
            views.update_assignment_question_list,
            name="assignment-edit-ajax",
        ),
        path(
            r"^assignment/edit/<int:assignment_id>$",
            views.AssignmentEditView.as_view(),
            name="assignment-edit",
        ),
        path(
            r"^question-search/$",
            views.question_search,
            name="question-search",
        ),
        # Standalone
        path(
            r"^live/access/(?P<token>[0-9A-Za-z=_-]+)/<assignment_hash>$",  # noqa
            views.live,
            name="live",
        ),
        path(
            r"^live/navigate/<int:assignment_id>/(?P<question_id>\d+)/(?P<direction>(next|prev|goto))/(?P<index>[0-9x]+)$",  # noqa
            views.navigate_assignment,
            name="navigate-assignment",
        ),
        path(
            r"^live/signup/form/<group_hash>$",
            views.signup_through_link,
            name="signup-through-link",
        ),
        path(
            r"^live/studentgroupassignment/create/<int:assignment_id>$",
            views.StudentGroupAssignmentCreateView.as_view(),
            name="student-group-assignment-create",
        ),
        # Admin
        path(r"^dashboard/$", views.dashboard, name="dashboard"),
        path(
            r"^admin/$",
            admin_views.AdminIndexView.as_view(),
            name="admin-index",
        ),
        path(
            r"^admin/peerinst/",
            include(
                [
                    path(
                        r"^assignment_results/<int:assignment_id>/",
                        include(
                            [
                                path(
                                    r"^$",
                                    admin_views.AssignmentResultsView.as_view(),  # noqa
                                    name="assignment-results",
                                ),
                                path(
                                    r"^rationales/(?P<question_id>\d+)$",
                                    admin_views.QuestionRationaleView.as_view(),  # noqa
                                    name="question-rationales",
                                ),
                            ]
                        ),
                    ),
                    path(
                        r"^question_preview/<int:question_id>$",
                        admin_views.QuestionPreviewView.as_view(),
                        name="question-preview",
                    ),
                    path(
                        r"^fake_usernames/$",
                        admin_views.FakeUsernames.as_view(),
                        name="fake-usernames",
                    ),
                    path(
                        r"^fake_countries/$",
                        admin_views.FakeCountries.as_view(),
                        name="fake-countries",
                    ),
                    path(
                        r"^attribution_analysis/$",
                        admin_views.AttributionAnalysis.as_view(),
                        name="attribution-analysis",
                    ),
                    path(
                        r"^group_assignment_management/$",
                        admin_views.StudentGroupAssignmentManagement.as_view(),
                        name="group-assignment-management",
                    ),
                ]
            ),
        ),
        # Teachers
        path(
            r"^teacher-account/<int:pk>/$",
            views.TeacherDetailView.as_view(),
            name="teacher",
        ),
        path(
            r"^teacher/<int:pk>/$",
            views.TeacherUpdate.as_view(),
            name="teacher-update",
        ),
        path(
            r"^teacher/<int:pk>/assignments/$",
            views.TeacherAssignments.as_view(),
            name="teacher-assignments",
        ),
        path(
            r"^teacher/<int:pk>/blinks/$",
            views.TeacherBlinks.as_view(),
            name="teacher-blinks",
        ),
        path(
            r"^teacher/favourite",
            views.teacher_toggle_favourite,
            name="teacher-toggle-favourite",
        ),
        path(
            r"^teacher/<int:pk>/groups/$",
            views.TeacherGroups.as_view(),
            name="teacher-groups",
        ),
        path(
            r"^teacher/<int:pk>/group/<group_hash>/share$",  # noqa
            views.TeacherGroupShare.as_view(),
            name="group-share",
        ),
        path(
            r"^teacher/(?P<teacher_id>[0-9]+)/group_assignments/$",
            views.StudentGroupAssignmentListView.as_view(),
            name="group-assignments",
        ),
        path(
            r"^teacher/student_activity/$",
            views.student_activity,
            name="student-activity",
        ),
        path(
            r"^teacher/report/all_groups/<int:assignment_id>/$",
            views.report,
            name="report-all-groups",
        ),
        path(
            r"^teacher/report/all_assignments/(?P<group_id>[^/]+)/$",
            views.report,
            name="report-all-assignments",
        ),
        path(
            r"^teacher/report_selector$",
            views.report_selector,
            name="report_selector",
        ),
        path(r"^teacher/custom_report/$", views.report, name="report-custom"),
        path(
            r"^report_rationales_chosen$",
            views.report_assignment_aggregates,
            name="report_rationales_chosen",
        ),
        # Auth
        path(r"^$", views.landing_page, name="landing_page"),
        path(r"^signup/$", views.sign_up, name="sign_up"),
        path(
            r"^login/$",
            user_passes_test(not_authenticated, login_url="/welcome/")(
                auth_views.login
            ),
            name="login",
        ),
        path(r"^logout/$", views.logout_view, name="logout"),
        path(r"^welcome/$", views.welcome, name="welcome"),
        # Only non-students can change their password
        path(
            r"^password_change/$",
            user_passes_test(student_check)(password_views.password_change),
            name="password_change",
        ),
        path(
            r"^password_change/done/$",
            auth_views.password_change_done,
            name="password_change_done",
        ),
        path(
            r"^password_reset/$",
            auth_views.password_reset,
            {
                "html_email_template_name": "registration/password_reset_email_html.html",  # noqa
                "password_reset_form": NonStudentPasswordResetForm,
            },
            name="password_reset",
        ),
        path(
            r"^password_reset/done/$",
            auth_views.password_reset_done,
            name="password_reset_done",
        ),
        path(
            r"^reset/(?P<uidb64>[0-9A-Za-z_\-=]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",  # noqa
            password_views.password_reset_confirm,
            name="password_reset_confirm",
        ),
        path(
            r"^reset/done/$",
            auth_views.password_reset_complete,
            name="password_reset_complete",
        ),
        path(
            r"^terms_of_service/teachers/$",
            views.terms_teacher,
            name="terms_teacher",
        ),
        path(r"^access_denied/$", views.access_denied, name="access_denied"),
        path(
            r"^access_denied_and_logout/$",
            views.access_denied_and_logout,
            name="access_denied_and_logout",
        ),
        # Blink
        path(
            r"^blink/<int:pk>/$",
            views.BlinkQuestionFormView.as_view(),
            name="blink-question",
        ),
        path(
            r"^blink/<int:pk>/summary/$",
            views.BlinkQuestionDetailView.as_view(),
            name="blink-summary",
        ),
        path(
            r"^blink/<int:pk>/count/$", views.blink_count, name="blink-count",
        ),
        path(
            r"^blink/<int:pk>/close/$", views.blink_close, name="blink-close",
        ),
        path(
            r"^blink/<int:pk>/latest_results/$",
            views.blink_latest_results,
            name="blink-results",
        ),
        path(
            r"^blink/<int:pk>/reset/$", views.blink_reset, name="blink-reset",
        ),
        path(
            r"^blink/<int:pk>/status/$",
            views.blink_status,
            name="blink-status",
        ),
        path(
            r"^blink/<username>/$",
            views.blink_get_current,
            name="blink-get-current",
        ),
        path(
            r"^blink/<username>/url/$",
            cache_page(1)(views.blink_get_current_url),
            name="blink-get-current-url",
        ),
        path(
            r"^blink/<int:pk>/get_next/$",
            views.blink_get_next,
            name="blink-get-next",
        ),
        path(
            r"^blink/waiting/(?P<username>[\w.@+-]+)/$",
            views.blink_waiting,
            name="blink-waiting",
        ),
        path(
            r"^blink/waiting/<username>/<int:assignment>/$",
            views.blink_waiting,
            name="blink-waiting",
        ),
        path(
            r"^blinkAssignment/create/$",
            views.BlinkAssignmentCreate.as_view(),
            name="blinkAssignment-create",
        ),
        path(
            r"^blinkAssignment/<int:pk>/delete/$",
            views.blink_assignment_delete,
            name="blinkAssignment-delete",
        ),
        path(
            r"^blinkAssignment/<int:pk>/set_time/$",
            views.blink_assignment_set_time,
            name="blinkAssignment-set-time",
        ),
        path(
            r"^blinkAssignment/<int:pk>/start/$",
            views.blink_assignment_start,
            name="blinkAssignment-start",
        ),
        path(
            r"^blinkAssignment/<int:pk>/update/$",
            views.BlinkAssignmentUpdate.as_view(),
            name="blinkAssignment-update",
        ),
    ]


def group_patterns():
    return [
        path(
            r"^group/student-information/$",
            views.group.get_student_reputation,
            name="group-details--student-information",
        ),
        path(
            r"^group/<group_hash>/$",
            views.group_details_page,
            name="group-details",
        ),
        path(
            r"^group/<group_hash>/update/$",
            views.group_details_update,
            name="group-details-update",
        ),
        path(
            r"^group-assignment/<assignment_hash>/$",
            views.group_assignment_page,
            name="group-assignment",
        ),
        path(
            r"^group-assignment/<assignment_hash>/remove/$",
            views.group_assignment_remove,
            name="group-assignment-remove",
        ),
        path(
            r"^group-assignment/<assignment_hash>/update/$",
            views.group_assignment_update,
            name="group-assignment-update",
        ),
        path(
            r"^group-assignment/<assignment_hash>/send/$",
            views.send_student_assignment,
            name="send-student-assignment",
        ),
        path(
            r"^group-assignment/<assignment_hash>/student-progress/$",  # noqa
            views.get_assignment_student_progress,
            name="get-assignment-student-progress",
        ),
        path(
            r"^group-assignment/<assignment_hash>/" r"distribute/$",
            views.distribute_assignment,
            name="distribute-assignment",
        ),
    ]


def student_patterns():
    return [
        path(
            r"^assignment-complete/$",
            views.finish_assignment,
            name="finish-assignment",
        ),
        path(r"^student/$", views.student.index_page, name="student-page"),
        path(
            r"^student/join-group/$",
            views.student.join_group,
            name="student-join-group",
        ),
        path(
            r"^student/leave-group/$",
            views.student.leave_group,
            name="student-leave-group",
        ),
        path(
            r"^student/toggle-group-notifications/$",
            views.student.toggle_group_notifications,
            name="student-toggle-group-notifications",
        ),
        path(
            r"^student/login/$", views.student.login_page, name="student-login"
        ),
        path(
            r"^student/login-confirm/$",
            views.student.send_signin_link,
            name="student-send-signin-link",
        ),
        path(
            r"^student/remove-notification/$",
            views.student.remove_notification,
            name="student-remove-notification",
        ),
        path(
            r"^student/remove-notifications/$",
            views.student.remove_notifications,
            name="student-remove-notifications",
        ),
        path(
            r"^student/get-notifications/$",
            views.student.get_notifications,
            name="student-get-notifications",
        ),
        path(
            r"^student/update/student-id/$",
            views.student.update_student_id,
            name="student-change-id",
        ),
    ]


def search_patterns():
    return [
        path(r"^search/user$", views.search_users, name="search-users"),
        path(
            r"^search/category$",
            views.search_categories,
            name="search-categories",
        ),
    ]


def researcher_patterns():
    return [
        path(r"^research/$", views.research_index, name="research-index"),
        path(
            r"^research/discipline/<discipline_title>$",
            views.research_discipline_question_index,
            name="research-discipline-question-index-by-discipline",
        ),
        path(
            r"^research/assignment/<int:assignment_id>$",
            views.research_discipline_question_index,
            name="research-assignment-question-index-by-assignment",
        ),
        path(
            r"^research/all_scores/discipline/<discipline_title>/<int:question_pk>$",  # noqa
            views.research_all_annotations_for_question,
            name="research-all-annotations-for-question-by-discipline",
        ),
        path(
            r"^research/all_scores/assignment/<int:assignment_id>/<int:question_pk>$",  # noqa
            views.research_all_annotations_for_question,
            name="research-all-annotations-for-question-by-assignment",
        ),
        path(
            r"^research/discipline/<discipline_title>/<int:question_pk>/<int:answerchoice_value>$",  # noqa
            views.research_question_answer_list,
            name="research-question-answer-list-by-discipline",
        ),
        path(
            r"^research/assignment/<int:assignment_id>/<int:question_pk>/<int:answerchoice_value>$",  # noqa
            views.research_question_answer_list,
            name="research-question-answer-list-by-assignment",
        ),
        path(
            r"^research/question/flag/discipline/<discipline_title>/<int:question_pk>$",  # noqa
            views.flag_question_form,
            name="research-flag-question-by-discipline",
        ),
        path(
            r"^research/question/flag/assignment/<int:assignment_id>/<int:question_pk>$",  # noqa
            views.flag_question_form,
            name="research-flag-question-by-assignment",
        ),
        path(
            r"^expert/rationales/<int:question_id>$",
            admin_views.QuestionExpertRationaleView.as_view(),
            name="research-fix-expert-rationale",
        ),
        path(
            r"^research/assignment/<int:assignment_id>/expert/rationale/<int:question_id>$",  # noqa
            admin_views.QuestionExpertRationaleView.as_view(),
            name="research-fix-expert-rationale",
        ),
        path(
            r"^research/expert/rationale/fix/<int:pk>$",
            views.AnswerExpertUpdateView.as_view(),
            name="research-rationale-update-expert",
        ),
    ]


def collection_patterns():
    return [
        path(
            r"^collection/create/$",
            views.CollectionCreateView.as_view(),
            name="collection-create",
        ),
        path(
            r"^collection/<int:pk>$",
            views.CollectionDetailView.as_view(),
            name="collection-detail",
        ),
        path(
            r"^collection/update/<int:pk>$",
            views.CollectionUpdateView.as_view(),
            name="collection-update",
        ),
        path(
            r"^collection/delete/<int:pk>$",
            views.CollectionDeleteView.as_view(),
            name="collection-delete",
        ),
        path(
            r"^collection/list/$",
            views.CollectionListView.as_view(),
            name="collection-list",
        ),
        path(
            r"^collection/personal/$",
            views.PersonalCollectionListView.as_view(),
            name="personal-collection-list",
        ),
        path(
            r"^collection/followed/$",
            views.FollowedCollectionListView.as_view(),
            name="followed-collection-list",
        ),
        path(
            r"^collection/featured/$",
            views.FeaturedCollectionListView.as_view(),
            name="featured-collection-list",
        ),
        path(
            r"^collection/distribute/<int:pk>$",
            views.CollectionDistributeDetailView.as_view(),
            name="collection-distribute",
        ),
        path(
            r"^collection/follower",
            views.teacher_toggle_follower,
            name="teacher-toggle-follower",
        ),
        path(
            r"^collection/assignment",
            views.collection_toggle_assignment,
            name="collection-toggle-assignment",
        ),
        path(
            r"^collection/add/assignment",
            views.collection_add_assignment,
            name="collection-add-assignment",
        ),
        path(
            r"^collection/assign",
            views.collection_assign,
            name="collection-assign",
        ),
        path(
            r"^collection/unassign",
            views.collection_unassign,
            name="collection-unassign",
        ),
        path(
            r"^collection/collection-statistics",
            views.collection_statistics,
            name="collection-statistics",
        ),
        path(
            r"^collection/featured-data/$",
            views.featured_collections,
            name="collection-featured-data",
        ),
    ]


def teacher_patterns():
    return [
        path(
            r"^teacher/dashboard/$",
            views.teacher.dashboard,
            name="teacher-dashboard",
        ),
        path(
            r"^teacher/dashboard/new-questions/$",
            views.teacher.new_questions,
            name="teacher-dashboard--new-questions",
        ),
        path(
            r"^teacher/dashboard/rationales/evaluate$",
            views.teacher.evaluate_rationale,
            name="teacher-dashboard--evaluate-rationale",
        ),
        path(
            r"^teacher/dashboard/rationales/$",
            views.teacher.rationales_to_score,
            name="teacher-dashboard--rationales",
        ),
        path(
            r"^teacher/dashboard/collections/$",
            views.teacher.collections,
            name="teacher-dashboard--collections",
        ),
        path(
            r"^teacher/dashboard/messages/$",
            views.teacher.messages,
            name="teacher-dashboard--messages",
        ),
        path(
            r"^teacher/dashboard/dalite-messages/$",
            views.teacher.dalite_messages,
            name="teacher-dashboard--dalite-messages",
        ),
        path(
            r"^teacher/dashboard/dalite-messages/remove$",
            views.teacher.remove_dalite_message,
            name="teacher-dashboard--dalite-messages--remove",
        ),
        path(
            r"^teacher/dashboard/messages/read$",
            views.teacher.mark_message_read,
            name="teacher-dashboard--messages--read",
        ),
        path(
            r"^teacher/dashboard/unsubscribe-thread/$",
            views.teacher.unsubscribe_from_thread,
            name="teacher-dashboard--unsubscribe-thread",
        ),
        path(
            r"^teacher/gradebook/request/$",
            views.teacher.request_gradebook,
            name="teacher-gradebook--request",
        ),
        path(
            r"^teacher/gradebook/result/$",
            views.teacher.get_gradebook_task_result,
            name="teacher-gradebook--result",
        ),
        path(
            r"^teacher/gradebook/remove/$",
            views.teacher.remove_gradebook_task,
            name="teacher-gradebook--remove",
        ),
        path(
            r"^teacher/gradebook/download/$",
            views.teacher.download_gradebook,
            name="teacher-gradebook--download",
        ),
        path(
            r"^teacher/tasks/$", views.teacher.get_tasks, name="teacher-tasks"
        ),
    ]


def question_patterns():
    return [
        path(
            r"^question/flag/reasons$",
            views.question_.get_flag_question_reasons,
            name="question--flag--reasons",
        ),
        path(
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
