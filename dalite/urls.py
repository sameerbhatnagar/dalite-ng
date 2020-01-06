from django.conf import settings
from django.conf.urls import include
from django.urls import re_path
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.clickjacking import xframe_options_sameorigin

from . import views
from peerinst import views as peerinst_views

admin.site.site_header = admin.site.site_title = _("Dalite NG administration")

# LTI
urlpatterns = [re_path(r"^lti/", include("django_lti_tool_provider.urls"))]

# Apps
urlpatterns += i18n_patterns(
    re_path(
        r"^reputation/", include("reputation.urls", namespace="reputation")
    ),
    re_path(r"^quality/", include("quality.urls", namespace="quality")),
    re_path(r"^tos/", include("tos.urls")),
    re_path(r"", include("peerinst.urls")),
    re_path(
        r"^forums/", include("pinax.forums.urls", namespace="pinax_forums")
    ),
    re_path(
        r"^assignment/<int:assignment_id>/",
        include(
            [
                # Question table of contents for assignment - Enforce
                # sameorigin to prevent access from LMS
                re_path(
                    r"^$",
                    xframe_options_sameorigin(
                        peerinst_views.QuestionListView.as_view()
                    ),
                    name="question-list",
                ),
                re_path(
                    r"<int:question_id>/",
                    include(
                        [
                            # Dalite question
                            re_path(
                                r"^$", peerinst_views.question, name="question"
                            ),
                            # Question reset (for testing purposes) - Enforce
                            # sameorigin to prevent access from LMS
                            re_path(
                                r"^reset/$",
                                peerinst_views.reset_question,
                                name="reset-question",
                            ),
                        ]
                    ),
                ),
                re_path(
                    r"^update/$",
                    peerinst_views.AssignmentUpdateView.as_view(),
                    name="assignment-update",
                ),
            ]
        ),
    ),
    re_path(r"^grappelli/", include("grappelli.urls")),
    re_path(
        r"admin_index_wrapper/",
        views.admin_index_wrapper,
        name="admin_index_wrapper",
    ),
    re_path(r"^admin/", admin.site.urls),
)

# Set language view
urlpatterns += [re_path(r"^i18n/", include("django.conf.urls.i18n"))]

# Media
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Errors
#  handler400 = views.errors.response_400
#  handler403 = views.errors.response_403
handler404 = "dalite.views.errors.response_404"
#  handler500 = "dalite.views.errors.response_500"
