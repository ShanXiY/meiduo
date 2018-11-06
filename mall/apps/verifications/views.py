

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView

from libs.captcha.captcha import captcha
from libs.yuntongxun.sms import CCP
from . import constant


class RegisterImageCodeView(APIView):
    """
    # 2.接收前端提供的uuid
    # 3.生成图片验证码,保存 图片验证码的数据
    # 4.返回响应
    """
    def get(self,request,image_code_id):

        # 2.生成图片验证码
        text,image = captcha.generate_captcha()

        # 3.保存 图片验证码的数据
        redis_conn = get_redis_connection('code')
        redis_conn.setex('img_%s'%image_code_id,constant.IMAGE_CODE_EXPIRE_TIME,text)

        # 4.返回响应
        # return HttpResponse(image,content_type='application/json')
        return HttpResponse(image,content_type='image/jpeg')

from .serializers import RegisterSmscodeSerializer
class RegisterSmscodeView(APIView):

    def get(self,request,mobile):
        """
        # 1.接收前端数据
        # 2.校验数据，放到序列化器中
        # 3.生成短信验证码
        # 4.发送短信
        # 5.返回响应
        :param request:
        :param mobile:
        :return:
        """
        # 1.接收前端数据
        params = request.query_params

        # 2.校验数据，放到序列化器中
        #校验
        serializer = RegisterSmscodeSerializer(data=params)

        #调用is_vaild校验
        serializer.is_valid(raise_exception=True)

        # 3.生成短信验证码
        from random import randint
        sms_code = '%06d'%randint(0,999999)

        # 4.保存短信，发送短信
        redis_conn = get_redis_connection('code')
        redis_conn.setex('sms_%s'%mobile,300,sms_code)
        # CCP().send_template_sms(mobile,[5,sms_code],1)

        from celery_tasks.sms.tasks import send_sms_code

        #delay 的参数和send_sms_code 任务的参数是对应的
        send_sms_code.delay(mobile,sms_code)

        # 5.返回响应
        return Response({'msg':'ok'})
