from django.urls import path

from verification import views


urlpatterns = [
    path('<group>/<key>/success/', views.claim_success, name='verification-success'),
    path('<group>/<key>/post/',    views.claim_post_url, name='verification-claim-post-url'),
    path('<group>/<key>/get/',     views.claim_get, name='verification-claim-get'),
]
