from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'username': user.username,
        'user_id':user.id
    }

from django.contrib.auth.backends import ModelBackend

import re

class MobileUsernameModelBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            #1.根据username查询用户信息
            if re.match('1[3-9]\d{9}',username):
                #手机号
                user = User.objects.get(mobile=username)
            else:
                #用户名
                user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        #2.校验用户的密码
        if user.check_password(password):
            return user

