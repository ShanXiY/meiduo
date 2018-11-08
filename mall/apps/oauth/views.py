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
from mall import settings

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


"""
前段应该 在用户扫描完成之后,跳转到 http://www.meiduo.site:8080/oauth_callback.html?code=6E2E3F64C34ECFE29222EBC390D29196&state=test
把code 传递给后端,

GET     /oauth/qq/users/?code=xxx

# 1.我们获取到这个code, 通过接口来换去 token
# 2.有了token,就可以换取 oepnid


"""
from rest_framework import status

class OauthQQUserView(APIView):
    def get(self,request):
        code = request.query_params.get('code')

        if code is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        #1.我们获取到这个code，通过接口来换取token
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)

        access_token = oauth.get_access_token(code)

        #2.有token就可以换取openid
        openid = oauth.get_open_id(access_token)

        pass


