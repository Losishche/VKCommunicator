"""VKSpammer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
]

#и тут почему-то. Блин, непонятно
urlpatterns = patterns('',

    #Значок доллара в конце не нужен, тк ЭТО КОНЕЦ СТРОКИ!!
    url(r'^VKCommunicator/', include('VKSpam_djg.urls', namespace="VKSpam_djg")),
    #url(r'^VKCommunicator/$', include('VKSpammer.urls', namespace="VKSpammer")),
    #url(r'^VKCommunicator/statistics/$', 'VKSpam_djg.views.statistics'),
    #url(r'^VKCommunicator/(?P<vk_group_id>\d+)/$', 'VKSpam_djg.views.detail'),
    #url(r'^VKCommunicator/(?P<vk_group_id>\d+)/results/$', 'VKCommunicator.views.results'),
    #url(r'^VKCommunicator/(?P<vk_group_id>\d+)/vote/$', 'VKCommunicator.views.vote'),
    url(r'^admin/', include(admin.site.urls)),
)
