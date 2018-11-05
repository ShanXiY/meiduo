from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.views import APIView

from libs.captcha.captcha import captcha
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