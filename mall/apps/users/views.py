from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import SKU
from users.models import User
from users.serializers import RegisterCreateUserSerializer, SKUSerializer
from users.utils import generic_active_url, get_active_user


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



"""
用户在点击设置的时候,输入 邮箱信息, 当点击保存的时候 需要将邮箱信息发送给后端


# 1. 这个接口必须是登录才可以访问
# 2. 接收参数
# 3. 验证数据
# 4. 更新数据
# 5. 发送激活邮件
# 6. 返回响应

PUT         /users/emails/


"""
from .serializers import UserEmailSerializer
from rest_framework.mixins import UpdateModelMixin
from django.conf import settings

class UserEmailView(APIView):

    # 1. 这个接口必须是登录才可以访问
    permission_classes = [IsAuthenticated]

    def put(self,request):
        # 2. 接收参数
        data = request.data

        # 3. 验证数据
        user = request.user
        serializer = UserEmailSerializer(instance=user,data=data)
        serializer.is_valid(raise_exception=True)

        # 4. 更新数据
        serializer.save()

        from celery_tasks.email.tasks import send_active_email
        send_active_email.delay(data.get('email'),request.user.id)

        # 5. 发送激活邮件
        # from django.core.mail import send_mail
        #
        # subject = '美多商城激活邮件' #主题
        #
        # message = '内容' #内容
        #
        # from_email = settings.EMAIL_FROM #发件人
        #
        # email = data.get('email')
        # recipient_list = [email]  #接收人列表
        #
        # #可以设置一些html的样式等信息
        # verify_url = generic_active_url(user.id,email)
        #
        # html_message = '<p>尊敬的用户您好！</p>' \
        #            '<p>感谢您使用美多商城。</p>' \
        #            '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
        #            '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)
        #
        # send_mail(
        #     subject=subject,
        #     message=message,
        #     from_email=from_email,
        #     recipient_list=recipient_list,
        #     html_message=html_message
        # )


        # 6. 返回响应
        return Response(serializer.data)


# from .serializers import UserEmailSerializer
# class UserCenterEmailView(APIView):
#
#
#     permission_classes = [IsAuthenticated]
#
#     def put(self,request):
#         # 2. 接收参数
#         data = request.data
#         user = request.user
#         # 3. 验证数据 -- 序列化器
#         serializer = UserEmailSerializer(instance=user,data=data)
#         serializer.is_valid(raise_exception=True)
#         # 4. 更新数据
#         serializer.save()
#         # 5. 发送激活邮件
#         # 6. 返回响应
#         return Response(serializer.data)

from rest_framework import status
class UserActiveEmailView(APIView):
    """

        当用户点击激活连接的时候,会跳转到一个页面,这个页面中含有 token(含有 用户id和email信息)信息
        前端需要发送一个ajax请求,将 token 发送给后端

        # 1. 接受token
        # 2. 对token进行解析
        # 3. 返回响应

        GET     /users/emails/verification/?token=xxx
        """
    def get(self,request):

        # 1. 接受token
        token = request.query_params.get('token')
        if token is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)


        # 2. 对token进行解析
        user = get_active_user(token)
        if user is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user.email_active=True
        user.save()

        # 3. 返回响应
        return Response({'msg':'ok'})

"""

新增地址功能

前端将用户提交的数据 传递给后端

1.后端接受数据
2.对数据进行校验
3.数据入库
4.返回响应

POST    users/addresses/

"""

from rest_framework.generics import CreateAPIView
from .serializers import AddressSerializer
from rest_framework.generics import GenericAPIView

class AddressCreateAPIView(CreateAPIView):
    serializer_class = AddressSerializer

"""
修改标题
PUT    users/address/title/

"""

from rest_framework.decorators import action
from .serializers import AddressTitleSerializer


@action(methods=['put'], detail=True)
def title(self, request, pk=None, address_id=None):
    """
    修改标题
    """
    address = self.get_object()
    serializer = AddressTitleSerializer(instance=address, data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

from rest_framework import mixins
from rest_framework.generics import GenericAPIView
from .serializers import  AddUserBrowsingHistorySerializer
from rest_framework.permissions import IsAuthenticated

# class UserBrowsingHistoryView(mixins.CreateModelMixin, GenericAPIView):
#     """
#     用户浏览历史记录
#     POST /users/browerhistories/
#     GET  /users/browerhistories/
#     数据只需要保存到redis中
#     """
#     serializer_class = AddUserBrowsingHistorySerializer
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request):
#         """
#         保存
#         """
#         return self.create(request)
#
#     def get(self, request):
#         """获取"""
#         # 获取用户信息
#         user_id = request.user.id
#         # 连接redis
#         redis_conn = get_redis_connection('history')
#         # 获取数据
#         history_sku_ids = redis_conn.lrange('history_%s' % user_id, 0, 5)
#         skus = []
#         for sku_id in history_sku_ids:
#             sku = SKU.objects.get(pk=sku_id)
#             skus.append(sku)
#         # 序列化
#         serializer = SKUSerializer(skus, many=True)
#         return Response(serializer.data)


# class UserHistoryView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self,request):
#         user = request.user
#         #1.接收数据，对数据进行校验
#         serializer = AddUserBrowsingHistorySerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         #2.保存数据  --redis 连接redis
#         redis_con = get_redis_connection('history')
#
#         #2.1获取商品id
#         sku_id = serializer.validated_data.get('sku_id')
#
#         #2.2先删除 sku_id 原因是为了去重
#         redis_con.lrem('history_%s'%user.id,sku_id)
#
#         #2.3保存到redis中
#         redis_con.lpush('history_%s'%user.id,sku_id)
#
#         #2.4对列表进行修剪
#         redis_con.ltrim('history_%s'%user.id,0,4)
#
#         #3.返回响应
#         return Response(serializer.data)
#     def get(self,request):
#         #1.接收数据(用户信息，以jwt的形式传递)
#         user = request.user
#         #2.查询数据
#         redis_conn = get_redis_connection('history')
#
#         sku_ids = redis_conn.lrange('history_%s'%user.id,0,5)
#
#         skus = []
#         for sku_id in sku_ids:
#             sku = SKU.objects.get(id=sku_id)
#             skus.append(sku)
#
#         serializer = SKUSerializer(skus,many=True)
#
#         #3.返回响应
#         return Response(serializer.data)
#


from rest_framework.mixins import CreateModelMixin

class UserHistoryView(CreateModelMixin,GenericAPIView):

    serializer_class = AddUserBrowsingHistorySerializer

    def post(self,request):

        return self.create(request)

    def get(self, request):
        """获取"""
        # 获取用户信息
        user_id = request.user.id
        # 连接redis
        redis_conn = get_redis_connection('history')
        # 获取数据
        history_sku_ids = redis_conn.lrange('history_%s' % user_id, 0, 5)
        skus = []
        for sku_id in history_sku_ids:
            sku = SKU.objects.get(pk=sku_id)
            skus.append(sku)
        # 序列化
        serializer = SKUSerializer(skus, many=True)
        return Response(serializer.data)