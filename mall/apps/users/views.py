from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User


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


