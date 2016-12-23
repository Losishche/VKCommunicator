from django.contrib import admin

from VKSpam_djg.models import VkGroupUserUnion
from VKSpam_djg.models import CampParams, BotsSenders, PrivatMessages, VkErrorText, AvaMessages
from django.contrib import admin

admin.site.register(VkGroupUserUnion)
admin.site.register(CampParams)
admin.site.register(BotsSenders)
admin.site.register(PrivatMessages)
admin.site.register(AvaMessages)