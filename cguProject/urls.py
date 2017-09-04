"""cguProject URL Configuration

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
from django.conf.urls import url, include
from django.contrib import admin
from mainsite.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^$', index),
    url(r'^email_confirmation_success/$', email_confirmation_success),
    url(r'^makeNew/$', makeNew),
    url(r'^video/(\w+)/$', video),
    url(r'^follow/(\w+)/(\w+)/$', follow),
    url(r'^favorite/(\w+)/(\w+)/$', favorite),
    url(r'^modify/$', modify),
    url(r'^aftermodify/$',aftermodify),
    url(r'^autoAL/$', autoAL, name='autoAL'),
    url(r'^songlist/(\w+)/$', songlist),
    url(r'^userinfo/(\w+)/$', userinfo),
    url(r'^userinfoedit/$', userinfoEdit),
]
