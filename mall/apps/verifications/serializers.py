from django_redis import get_redis_connection
from rest_framework import serializers

class RegisterSmscodeSerializer(serializers.Serializer):

    text = serializers.CharField(label='图片验证码',min_length=4,max_length=4,required=True)

    image_code_id = serializers.UUIDField(label='uuid',required=True)

    """
    校验：
    1.字段类型
    2.字段选项
    3.单个字段
    4.多个字段

    """
    def validate(self, attrs):
        """"
        # 1.用户提交的图片验证码
        # 2.获取redis验证码
        # 2.1连接redis
        # 2.2获取redis_text
        # 2.3判断是否过期
        # 3.比对
        # 4.校验完成 返回attrs
        """""
        # 1.用户提交的图片验证码
        text = attrs.get('text')
        image_code_id = attrs.get('image_code_id')

        # 2.获取redis验证码
        # 2.1连接redis
        redis_conn = get_redis_connection('code')

        # 2.2获取redis_text
        redis_text = redis_conn.get('img_%s'%image_code_id)

        # 2.3判断是否过期
        if redis_text is None:
            raise serializers.ValidationError('图片验证码已过期')

        # 3.比对
        if redis_text.decode().lower() != text.lower():
            raise serializers.ValidationError('图片验证码不一致')


        # 4.校验完成 返回attrs
        return attrs