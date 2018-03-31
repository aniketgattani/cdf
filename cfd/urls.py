"""cfd URL Configuration

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
from django.conf.urls import url
from django.contrib import admin
from cfd import views
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
 	url(r'^index', views.index),
 	url(r'^sw.js', (TemplateView.as_view(template_name="sw.js", content_type='application/javascript', ))),
    url(r'^login', views.login),
 	url(r'^signup', views.signup),
    url(r'^forgot', views.forgot),
    url(r'^logout', views.logout),
    url(r'^chating', views.interface),
 	url(r'^chat', views.chat),
    url(r'^message', views.sendMessage),
    url(r'^data', views.data),
    url(r'^emoji', views.emoji),
    url(r'^getUsers', views.getUsers),
    url(r'^suggest', views.suggestEmoji),
]
