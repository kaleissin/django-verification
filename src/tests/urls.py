from __future__ import unicode_literals

from django.conf.urls import include, url
from django.views.generic import TemplateView
from django.contrib.auth import views as authviews

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='index.html')),
    url(r'^', include('demo.projectapp.urls')),
    url(r'^verify/', include('verification.urls')),
#     url(r'^accounts/login/$', authviews.login, name='login'),
#     url(r'^accounts/logout/$', authviews.logout, name='logout'),
]
