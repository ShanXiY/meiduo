import re

from django_redis import get_redis_connection
from rest_framework import serializers
from users.models import User,Address


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
        fields = ('id','username','mobile','email','email_active')


class UserEmailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email',)


class AddressSerializer(serializers.ModelSerializer):

    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')



    def create(self, validated_data):

        #  我们并没有让前端传递用户的的 user_id 因为 我们是采用的jwt认证方式
        # 我们可以获取user_id 所以 validated_data 没有user_id
        # 但是我们在调用 系统的 crate方法的时候  Address.objects.create(**validated_data)
        # Address必须要 user_id 这个外键,所以就报错了
        # user = request.user
        validated_data['user'] = self.context['request'].user

        # return Address.objects.create(**validated_data)

        # super() 指向 单继承的 ModelSerializer
        return  super().create(validated_data)


class AddressTitleSerializer(serializers.ModelSerializer):
    """
    地址标题
    """
    class Meta:
        model = Address
        fields = ('title',)



from goods.models import SKU
from django_redis import get_redis_connection

class AddUserBrowsingHistorySerializer(serializers.Serializer):
    """
    添加用户浏览记录序列化器
    """
    sku_id = serializers.IntegerField(label='商品编号',min_value=1,required=True)

    def validate_sku_id(self,value):
        """
        检查商品是否存在
        """
        try:
            SKU.objects.get(pk=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')

        return value

    # def create(self, validated_data):
    #
    #     #获取用户信息
    #     user_id = self.context['request'].user.id
    #     #获取商品id
    #     sku_id = validated_data['sku_id']
    #     #连接redis
    #     redis_conn = get_redis_connection('history')
    #     #移除已经存在的本记录
    #     redis_conn.lrem('history_%s'%user_id,0,sku_id)
    #     #添加新的记录
    #     redis_conn.lpush('history_%s'%user_id,sku_id)
    #     #保存最多5条记录
    #     redis_conn.ltrim('history_%s'%user_id,0,4)
    #     return validated_data


    def create(self, validated_data):

        user = self.context['request'].user

        redis_con = get_redis_connection('history')

        # 2.1 获取商品id
        sku_id = validated_data.get('sku_id')

        # 2.2 先删除 这个 sku_id  为什么删除呢? 去重
        redis_con.lrem('history_%s' % user.id, 0, sku_id)

        # 2.3 保存到redis中
        redis_con.lpush('history_%s' % user.id, sku_id)

        # 2.4对列表进行修剪
        redis_con.ltrim('history_%s' % user.id, 0, 4)

        return validated_data


class SKUSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = ('id', 'name', 'price', 'default_image_url', 'comments')
