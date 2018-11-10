import re

from django_redis import get_redis_connection
from rest_framework import serializers
from users.models import User


"""
serializers.ModelSerializer
serializerss.Serializer

数据入库 选择 ModelSerializer 肯定有 模型
"""

class RegisterCreateUserSerializer(serializers.ModelSerializer):
    """
    6个参数(username,password,password2,mobile,sms_code,allow)
    """

    sms_code = serializers.CharField(label='短信验证码',min_length=6,max_length=6,write_only=True)
    password2 = serializers.CharField(label='确认密码',write_only=True)
    allow = serializers.CharField(label='是否同意协议',write_only=True)

    token = serializers.CharField(label='token',read_only=True)

    #ModelSerializer 自动生成字段的时候是根据fields列表生成的
    class Meta:
        model = User
        fields = ['username','password','mobile','sms_code','password2','allow','token']

        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    """
    1.字段类型
    2.字段选项
    3.单个字段
    4，多个字段

    1.手机号校验，密码一致，短信校验，是否同意

    手机号就是规则 单个字段
    是否同意    单个字段
    密码一致，短信校验       多个字段

    """

    def validate_mobile(self,value):
        if not re.match('1[3-9]\d{9}',value):
            raise serializers.ValidationError('手机号格式不满足要求')


        #校验之后最终要返回回去
        return value

    def validate_allow(self,value):
        if value == 'false':
            raise serializers.ValidationError('您未同意协议')

        return value

    def validate(self, attrs):
        #1.密码一致
        password = attrs.get('password')
        password2 = attrs.get('password2')
        mobile = attrs.get('mobile')
        sms_code = attrs.get('sms_code')


        if password != password2:
            raise serializers.ValidationError('密码不一致')

        #2.短信
        redis_conn = get_redis_connection('code')
        sms_code_redis = redis_conn.get('sms_%s'%mobile)
        if sms_code_redis is None:
            raise serializers.ValidationError('验证码已过期')

        if sms_code_redis.decode() != sms_code:
            raise serializers.ValidationError('验证码错误')
        return attrs

    def create(self, validated_data):
        #删除多余字段
        del validated_data['sms_code']
        del validated_data['password2']
        del validated_data['allow']

        user = User.objects.create(**validated_data)

        #对密码进行加密处理
        user.set_password(validated_data['password'])
        user.save()

        return user

class UserCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username','mobile','email',)