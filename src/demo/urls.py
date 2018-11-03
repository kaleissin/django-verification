from __future__ import unicode_literals

from django import VERSION
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls import include, url
from django.views.generic import TemplateView
from django.contrib.auth import views as authviews

urlpatterns = static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if VERSION[:2] < (1, 9):  # Django < 1.9
    urlpatterns += [url(r'^admin/', include(admin.site.urls))]
else:
    urlpatterns += [url(r'^admin/', admin.site.urls)]

urlpatterns += [
    url(r'^$', TemplateView.as_view(template_name='index.html')),
    url(r'^', include('demo.projectapp.urls')),
    url(r'^verify/', include('verification.urls')),
    url(r'^accounts/login/$', authviews.login, name='login'),
    url(r'^accounts/logout/$', authviews.logout, name='logout'),
]
