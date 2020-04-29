"""auctionsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views
from django.contrib.auth import views as django_auth_views


urlpatterns = [
    url(r'^admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    url(r'^giaadmin/', admin.site.urls),
    url(r'^search/', include('haystack.urls')),
    url(r'^password_change/$', django_auth_views.PasswordChangeView.as_view(), name='password_change'),
    url(r'^password_change/done/$', django_auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^', include('items.urls', namespace="items")),
]

# Adding Static File Urls (for Dev environment only)
urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
