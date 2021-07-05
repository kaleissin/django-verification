from django.urls import path

from demo.projectapp import views


urlpatterns = [
    path('delete/', views.delete_user, name='delete_user'),
    path('create/', views.create_user, name='create_user'),
    path('create/get/', views.create_user_get, name='create_user_get'),
    path('create/get/', views.create_user_get, name='create_user_get'),
    path('create/post/', views.create_user_post, name='create_user_post'),
    path('create/post/password/', views.create_user_post_password, name='create_user_post_password'),
    path('verify/<group>/<key>/form/',  views.claim_post_form, name='demo-claim-postform'),
    path('verify/simple/',  views.claim, name='demo-claim'),
]
