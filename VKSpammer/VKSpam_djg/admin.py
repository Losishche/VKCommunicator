from VKSpam_djg.models import VkGroupUserUnion
from VKSpam_djg.models import CampParams, BotsSenders, PrivateMessages, VkErrorText, AvaMessages, VKApplications
from VKSpam_djg.models import OkBotsSenders, InvitePrivateMessages, InviteMessagesToLoyalGroupUsers, VkAudioParams
from django.contrib import admin

admin.site.register(VkGroupUserUnion)
admin.site.register(CampParams)
admin.site.register(BotsSenders)
admin.site.register(PrivateMessages)
admin.site.register(AvaMessages)
admin.site.register(VKApplications)
admin.site.register(VkAudioParams)
admin.site.register(OkBotsSenders)
admin.site.register(InvitePrivateMessages)
admin.site.register(InviteMessagesToLoyalGroupUsers)
