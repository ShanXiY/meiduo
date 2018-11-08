from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response

"""
1. 获取code
2. 通过code换取token
3. 通过token 换去 openid

GET   /oauth/qq/statues/
"""

from rest_framework.views import APIView
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
# from mall import settings

class OauthQQURLView(APIView):

    def get(self,request):

        state = 'test'

        #1.创建oauth对象
        #client_id=None, client_secret=None, redirect_uri=None, state=None
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=state)

        #2.调用方法，获取url
        login_url = oauth.get_qq_url()

        return Response({"login_url":login_url})


