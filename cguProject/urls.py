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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from mainsite.views import *


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^$', home),
	url(r'^index/$', index),
    url(r'^email_confirmation_success/$', email_confirmation_success),
    url(r'^makeNew/$', makeNew),
    url(r'^video/(\w+)/$', video),
    url(r'^like/(\w+)/$', like),
    url(r'^follow/(\w+)/$', follow),
    url(r'^favorite/(\w+)/$', favorite),
    url(r'^comment/(\w+)/$', comment),
    url(r'^modify_text/(\w+)/$', modify_text),
    url(r'^modify/$', modify),
    url(r'^aftermodify/$',aftermodify),
    url(r'^autoAL/$', autoAL, name='autoAL'),
    url(r'^TagFounder/$', TagFounder, name='TagFounder'),
    url(r'^songlist/(\w+)/$', songlist),
    url(r'^userinfo/(\w+)/(\w+)$', userinfo),
    url(r'^userinfoedit/$', userinfoEdit),
    url(r'^uploadImage/$', uploadImage),
    url(r'^deleteImage/$', deleteImage),
	url(r'^home/$', home),
    url(r'^search/$', songSearch)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
