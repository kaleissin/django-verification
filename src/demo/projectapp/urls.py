from django.conf.urls import patterns, include, url

GROUP_RE = r'(?P<group>[-\w]+)'
KEY_RE = r'(?P<key>[-\w]+)'

urlpatterns = patterns("demo.projectapp.views",
    url(r'^delete/$', 'delete_user', name='delete_user'),
    url(r'^create/get/$', 'create_user_get', name='create_user_get'),
    url(r'^create/post/$', 'create_user_post', name='create_user_post'),
    url(r'^create/post/password/$', 'create_user_post_password', name='create_user_post_password'),
    url(r'^verify/%s/%s/$' % (GROUP_RE, KEY_RE),  'claim_post_form', name='demo-claim-postform'),
)
