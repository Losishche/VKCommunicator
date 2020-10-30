__author__ = 'grishaev'
#import vk
import app_info
from time import sleep
from vk import exceptions

api = app_info.get_token()
#user_id = '367999823'
#api = app_info.get_token_from_db_bot(user_id)
group_id_for_inviting_from = 'gorkyvery'
group_id_to_invite_in = 'gorky_v_volgograde' # 'mgorkymumiytrollbar'
#group_number_id_in = 126912469
offset = 1000


group_number_id_in = api.groups.getById(group_ids =['gorky_v_volgograde'])[0]['gid']
print(group_number_id_in)
#sleep(300)
#members = app_info.final_getting_subscribers(api, group_id_for_inviting_from, offset=0)
members = api.groups.getMembers(
        group_id=group_id_for_inviting_from, fields=['can_write_private_message','sex','bdate','city'], offset=offset)
#print(members)

is_invited_users = api.groups.getInvitedUsers(group_id = group_number_id_in)[1:]
print(is_invited_users)

print(members['users'])

for users in members['users']:
    print(users)
    for invited_users in is_invited_users:
        #print(invited_users)
        if users['uid'] == invited_users['uid']:
            print(members['users'],"1")
            members['users'].remove(users)

for member in members['users']:
    print(member)

    try:
        result = api.groups.invite(group_id = group_number_id_in, user_id=member['uid'])
        print(result)
    except exceptions.VkAPIError as s:
        print("исключение")
        if s.message == 'Captcha needed':
            captcha_inputed = app_info.handling_captcha_exeption(s)
            result = api.groups.invite(
                group_id = 126912469,
                user_id=member['uid'],
                captcha_sid=s.error_data['captcha_sid'],
                captcha_key=captcha_inputed
            )
            print(result)

    sleep(1)


#api.groups.invite()