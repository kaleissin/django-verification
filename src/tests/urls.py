from django.urls import include, path
from django.views.generic import TemplateView
# from django.contrib.auth import views as authviews

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html')),
    path('/', include('demo.projectapp.urls')),
    path('verify/', include('verification.urls')),
    # path('accounts/login/', authviews.login, name='login'),
    # path('accounts/logout/', authviews.logout, name='logout'),
]
