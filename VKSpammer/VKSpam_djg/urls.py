# -*- coding: utf8 -*-
from django.conf.urls import url
from django.views.generic.base import TemplateView
from . import views
from django.views.generic import DetailView, ListView
from VKSpam_djg.models import CampParams


#в коммуникаторе шаблоны адресов пока ТУТ!!
urlpatterns = [

url(r'^$', views.index, name='index'),
url(r'^$', views.window_for_captcha, name='window_for_captcha'),
#url(r'^(?P<group_id>[a-zA-Z0-9]+)/statistics/$', views.statistics, name='statistics'),
#непонятно почему, но символ начала строки не нужен
url(r'works_with_groups/$', views.works_with_groups, name='works_with_groups'),
url(r'statistics/$', views.statistics, name='statistics'),
url(r'distr_to_avas/$', views.distr_to_avas, name='distr_to_avas'),
url(r'distr_to_walls/$', views.distr_to_walls, name='distr_to_walls',),
url(r'distr_to_privat/$', views.distr_to_privat, name='distr_to_privat',),
url(r'captcha_input_form/$', views.captcha_input_form, name='captcha_input_form'),
url(r'sender_bots/$', views.bots_senders_params, name='bots_senders'),  # здесь ИМЯ - ИМЯ ПЕРЕМЕННОЙ В ССЫЛКЕ ФОРМЫ В ШАБЛОНЕ!!!
url(r'get_set_of_tokens/$', views.get_set_of_tokens, name='get_set_of_tokens'),
#url(r'start_campaign/$', views.start_campaign, name='start_campaign'),

url(r'start_campaign/$',
        ListView.as_view(
            queryset=CampParams.objects.all(),
            context_object_name='campaign_list',
            template_name='VKSpam_djg/set_up_campaigns.html')),
]
