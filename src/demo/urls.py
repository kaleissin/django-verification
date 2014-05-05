from __future__ import unicode_literals

from django.contrib import admin

from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

urlpatterns = staticfiles_urlpatterns()

urlpatterns += patterns("",
    url(r'^$', TemplateView.as_view(template_name='index.html')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('demo.projectapp.urls')),
    url(r'^verify/', include('verification.urls')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', name='logout'),
)
