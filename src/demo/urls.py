from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from django.urls import include, path
from django.views.generic import TemplateView
from django.contrib.auth import views as authviews

urlpatterns = static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [path('admin/', admin.site.urls)]

urlpatterns += [
    path('', TemplateView.as_view(template_name='index.html')),
    path('/', include('demo.projectapp.urls')),
    path('verify/', include('verification.urls')),
    path('accounts/login/', authviews.LoginView.as_view(), name='login'),
    path('accounts/logout/', authviews.LogoutView.as_view(), name='logout'),
]
