from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.serializers import RegisterCreateUserSerializer


class RegisterUsernameCountView(APIView):
    def get(self,request,username):
        """
        2.后端接收用户名
        3.查询校验是否重复
        4.返回响应
        :param request:
        :param username:
        :return:
        """
        # 2.后端接收用户名
        # 3.查询校验是否重复
        #count = 0 表示没有注册
        #count = 1 表示注册
        count = User.objects.filter(username=username).count()

        # 4.返回响应
        return Response({'count':count,'username':username})

"""
前端应该将6个参数(username,password,password2,mobile,sms_code,allow)传递给后端

# 1.接收前端提交的数据
# 2,校验数据
# 3.数据入库
# 4.返回响应

POST    users/
APIView
GenericAPIView      列表，详情通用支持，一般和mixin配合使用
CreateAPIView

"""
from  rest_framework.mixins import CreateModelMixin
from rest_framework.generics import CreateAPIView
from rest_framework_jwt.utils import jwt_response_payload_handler

class RegisterCreateUserView(APIView):

    def post(self,request):

        # 1.接收前端提交的数据
        data = request.data

        # 2,校验数据
        serializer = RegisterCreateUserSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        # 3.数据入库
        serializer.save()

        # 4.返回响应
        return Response(serializer.data)


from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User
# Create your views here.

class RegisterPhoneCountAPIView(APIView):
    """
    查询手机号的个数
    GET: /users/phones/(?P<mobile>1[345789]\d{9})/count/
    """
    def get(self,request,mobile):

        #通过模型查询获取手机号个数
        count = User.objects.filter(mobile=mobile).count()
        #组织数据
        context = {
            'count':count,
            'phone':mobile
        }

        return Response(context)

