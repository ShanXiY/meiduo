from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'username': user.username,
        'user_id':user.id
    }

from django.contrib.auth.backends import ModelBackend

import re
"""
1. n行代码实现了一个功能(方法) 我们就可以将代码抽取(封装)出去
2. 如果多次出现的代码(第二次出现,就抽取)

 抽取(封装)的思想是:
    1.将要抽取的代码 原封不动的放到一个函数中,函数暂时不需要参数
    2.抽取的代码 哪里有问题 改哪里, 其中的变量,定义为函数的参数
    3.用抽取的函数 替换  原代码,进行测试

"""
def get_user(username):
    try:
        # 1.根据username查询用户信息
        if re.match('1[3-9]\d{9}', username):
            # 手机号
            user = User.objects.get(mobile=username)
        else:
            # 用户名
            user = User.objects.get(username=username)
    except User.DoesNotExist:
        return None

    return user


class MobileUsernameModelBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        # try:
        #     #1.根据username查询用户信息
        #     if re.match('1[3-9]\d{9}',username):
        #         #手机号
        #         user = User.objects.get(mobile=username)
        #     else:
        #         #用户名
        #         user = User.objects.get(username=username)
        # except User.DoesNotExist:
        #     return None
        user = get_user(username)
        #2.校验用户的密码
        if user.check_password(password):
            return user
        return None

class SettingBackend(object):
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
        # 2.校验用户的密码
        if user.check_password(password):
            return user

    def get_user(self,user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

