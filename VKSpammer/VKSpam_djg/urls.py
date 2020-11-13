# -*- coding: utf8 -*-
from django.conf.urls import url
from django.views.generic.base import TemplateView
from . import views
from django.views.generic import DetailView, ListView
from VKSpam_djg.models import CampParams

app_name='VKSpam_djg'

#в коммуникаторе шаблоны адресов пока ТУТ!!
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^$', views.window_for_captcha, name='window_for_captcha'),
    # url(r'^(?P<group_id>[a-zA-Z0-9]+)/statistics/$', views.statistics, name='statistics'),
    # непонятно почему, но символ начала строки не нужен
    url(r'works_with_groups/$', views.works_with_groups, name='works_with_groups'),
    url(r'statistics/$', views.statistics, name='statistics'),
    url(r'distr_to_avas/$', views.distr_to_avas, name='distr_to_avas'),
    url(r'distr_to_walls/$', views.distr_to_walls, name='distr_to_walls',),
    url(r'distr_to_privat/$', views.distr_to_privat, name='distr_to_privat',),
    url(r'captcha_input_form/$', views.captcha_input_form, name='captcha_input_form'),
    # здесь ИМЯ - ИМЯ ПЕРЕМЕННОЙ В ССЫЛКЕ ФОРМЫ В ШАБЛОНЕ!!!
    url(r'sender_bots/$', views.bots_senders_params, name='bots_senders'),
    url(r'get_set_of_tokens/$', views.get_set_of_tokens, name='get_set_of_tokens'),
    url(
        r'make_distribution_to_friends_private/',
        views.make_distribution_to_friends_private,
        name='make_distribution_to_friends_private'
    ),
    url(
        r'make_distribution_to_aim_group_users/',
        views.make_distribution_to_aim_group_users,
        name='make_distribution_to_aim_group_users'
    ),
    url(
        r'make_distribution_in_privat_through_fake_browser/',
        views.make_distribution_in_privat_through_fake_browser,
        name='make_distribution_in_privat_through_fake_browser'
    ),
    # url(r'start_campaign/$', views.start_campaign, name='start_campaign'),
    url(
        r'start_campaign/$',
        ListView.as_view(
            queryset=CampParams.objects.all(),
            context_object_name='campaign_list',
            template_name='VKSpam_djg/set_up_campaigns.html')
    ),
    url(r'working_with_aim_group/$', views.working_with_aim_group, name='working_with_aim_group'),
    url(r'get_aim_group_wall_posts/$', views.get_aim_group_wall_posts, name='get_aim_group_wall_posts'),
    url(r'add_bots_to_eachother_friends/$', views.add_bots_to_eachother_friends, name='add_bots_to_eachother_friends'),
    url(r'like_aim_group_wall_post_through_fake_browser/$',
        views.like_aim_group_wall_post_through_fake_browser,
        name='like_aim_group_wall_post_through_fake_browser')

]

