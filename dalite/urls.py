from django.conf import settings
from django.conf.urls import include
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.i18n import JavaScriptCatalog

from . import views
from peerinst import views as peerinst_views

admin.site.site_header = admin.site.site_title = _(
    "SALTISE admin site for mydalite.org "
)


# LTI
urlpatterns = [path("lti/", include("django_lti_tool_provider.urls"))]

# Apps
urlpatterns += i18n_patterns(
    path(
        "feedback/", include("user_feedback.urls", namespace="user_feedback")
    ),
    path("course-flow/", include("course_flow.urls", namespace="course_flow")),
    path("reputation/", include("reputation.urls", namespace="reputation")),
    path("quality/", include("quality.urls", namespace="quality")),
    path("tos/", include("tos.urls")),
    path("rest-api/", include("REST.urls", namespace="REST")),
    path(r"", include("peerinst.urls")),
    path("forums/", include("pinax.forums.urls", namespace="pinax_forums")),
    path(
        "assignment/<assignment_id>/",
        include(
            [
                # Question table of contents for assignment - Enforce
                # sameorigin to prevent access from LMS
                path(
                    "",
                    xframe_options_sameorigin(
                        peerinst_views.QuestionListView.as_view()
                    ),
                    name="question-list",
                ),
                path(
                    r"<int:question_id>/",
                    include(
                        [
                            # Dalite question
                            path("", peerinst_views.question, name="question"),
                            # Question reset (for testing purposes) - Enforce
                            # sameorigin to prevent access from LMS
                            path(
                                "reset/",
                                peerinst_views.reset_question,
                                name="reset-question",
                            ),
                        ]
                    ),
                ),
                path(
                    "update/",
                    peerinst_views.AssignmentUpdateView.as_view(),
                    name="assignment-update",
                ),
            ]
        ),
    ),
    path("grappelli/", include("grappelli.urls")),
    path(
        r"admin_index_wrapper/",
        views.admin_index_wrapper,
        name="admin_index_wrapper",
    ),
    path("admin/", admin.site.urls),
)

# Set language view
urlpatterns += [path("i18n/", include("django.conf.urls.i18n"))]

# Javascript translations
urlpatterns += i18n_patterns(
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
)

# Media
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Security check in development
# if settings.DEBUG:
#     from security_headers.views import scan_url
#     urlpatterns += i18n_patterns(
#         re_path(r"^security/(?P<url_name>[\w-]+)/", scan_url, name="scan")
#     )

# Errors
#  handler400 = views.errors.response_400
#  handler403 = views.errors.response_403
handler404 = "dalite.views.errors.response_404"
#  handler500 = "dalite.views.errors.response_500"
