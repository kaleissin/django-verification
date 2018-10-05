from __future__ import unicode_literals

from django.conf.urls import *

from verification import views


GROUP_RE = r'(?P<group>[-\w]+)'
KEY_RE = r'(?P<key>[-\w]+)'

urlpatterns = [
    url(r'^%s/%s/success/$' % (GROUP_RE, KEY_RE), views.claim_success, name='verification-success'),
    url(r'^%s/%s/post/$' % (GROUP_RE, KEY_RE),  views.claim_post_url, name='verification-claim-post-url'),
    url(r'^%s/%s/get/$' % (GROUP_RE, KEY_RE),   views.claim_get, name='verification-claim-get'),
]
