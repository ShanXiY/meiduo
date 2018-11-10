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

from rest_framework.permissions import IsAuthenticated
from .serializers import UserCenterSerializer
# class UserCenterView(APIView):
#     """
#        登录用户访问个人中心的时候 ,我们需要将个人信息返回获取
#
#        1. 如何确定是登录用户  --> 需要前端传递一个token过来
#        2. 获取用户信息
#        3. 返回数据
#
#        GET     /users/infos/
#        """
#     #权限
#     #1.登录用户访问
#     # permission_classes = [IsAuthenticated]
#     #
#     # #2.获取用户信息
#     # def get(self,request):
#     #     user = request.user
#     #     #3.返回数据
#     #     serializer = UserCenterSerializer(user)
#     #     return Response(serializer.data)


from rest_framework.mixins import RetrieveModelMixin
from rest_framework.generics import RetrieveAPIView
class UserCenterView(RetrieveAPIView):

    serializer_class = UserCenterSerializer

    queryset = User.objects.all()

    #权限
    permission_classes = [IsAuthenticated]

    def get_object(self):
        #获取某一个指定的对象

        return self.request.user

