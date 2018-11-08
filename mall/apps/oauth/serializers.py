from rest_framework import serializers

from oauth.utils import check_open_id
from .models import OAuthQQUser
from django_redis import get_redis_connection

"""
    用户点击绑定按钮的时候,前端应该将 手机号,密码,openid,sms_code 发送给后端


    2. 对数据进行校验
        2.1 校验 openid 和sms_code
        2.2 判断手机号
            如果注册过,需要判断 密码是否正确
            如果没有注册过,创建用户
    3. 保存数据
        3.1保存 user 和 openid

    """
class OauthQQUserSerializer(serializers.Serializer):
    access_token = serializers.CharField(label='操作凭证')
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')
    password = serializers.CharField(label='密码', max_length=20, min_length=8)
    sms_code = serializers.CharField(label='短信验证码')

    def validate(self, attrs):
        #1.1校验 openid
        openid = check_open_id(attrs.get('access_token'))
        if openid is None:
            raise serializers.ValidationError('access_token错误')
        #1.2 sms_code

        sms_code= attrs.get('sms_code')
        redis_conn = get_redis_connection('code')

        redis_code = redis_conn.get('sms_%s'%attrs['mobile'])

        if redis_code is None:
            raise serializers.ValidationError('短信验证码已过期')

        if redis_code.decode() != sms_code:
            raise serializers.ValidationError('验证码不一致')
        # 1.3 判断手机号
        #     如果注册过,需要判断 密码是否正确
        #     如果没有注册过,创建用户

        return attrs