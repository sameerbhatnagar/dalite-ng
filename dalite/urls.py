# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

import views

admin.site.site_header = admin.site.site_title = _('Dalite NG administration')

#LTI
urlpatterns = [url(r'^lti/', include('django_lti_tool_provider.urls')),]

# Apps
urlpatterns = i18n_patterns(
    url(r'^tos/', include('tos.urls', namespace='tos')),
    url(r'', include('peerinst.urls')),
    url(r'^grappelli/', include('grappelli.urls')),
    url(
        r'admin_index_wrapper/',
        views.admin_index_wrapper,
        name='admin_index_wrapper',
    ),
    url(r'^admin/', include(admin.site.urls)),
)

# Set language view
urlpatterns += [url(r'^i18n/', include('django.conf.urls.i18n')),]

# Media
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
