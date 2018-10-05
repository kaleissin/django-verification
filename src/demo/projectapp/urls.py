from django.conf.urls import url

from demo.projectapp import views


GROUP_RE = r'(?P<group>[-\w]+)'
KEY_RE = r'(?P<key>[-\w]+)'

urlpatterns = [
    url(r'^delete/$', views.delete_user, name='delete_user'),
    url(r'^create/$', views.create_user, name='create_user'),
    url(r'^create/get/$', views.create_user_get, name='create_user_get'),
    url(r'^create/get/$', views.create_user_get, name='create_user_get'),
    url(r'^create/post/$', views.create_user_post, name='create_user_post'),
    url(r'^create/post/password/$', views.create_user_post_password, name='create_user_post_password'),
    url(r'^verify/%s/%s/form/$' % (GROUP_RE, KEY_RE),  views.claim_post_form, name='demo-claim-postform'),
    url(r'^verify/simple/$',  views.claim, name='demo-claim'),
]
