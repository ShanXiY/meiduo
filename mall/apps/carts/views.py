import base64
import pickle

from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response

from carts.serializers import CartSerializer, CartSKUSerializer
from django_redis import get_redis_connection

from goods.models import SKU

"""
1. 接收数据,对数据进行校验
2. 获取 sku_id,count,selected
3. 获取用户,根据用户信息判断登录状态
4. 登录用户redis
    4.1 连接redis
    4.2 保存数据到redis中
    4.3 返回响应
5. 未登录cookie
    5.1 先读取cookie数据,判断cookie中是否有购物车信息   str --> base64 -->pickle -->dict
        如果有则需要读取
        没有则不用管

    5.2 更新购物车信息  dict

    5.3 需要对购物车信息进行处理 dict --> pickle --> base64 -->str

    5.4 返回响应
"""

from rest_framework.views import APIView

class CartView(APIView):
    # 如果传递的token有问题,就不能实现 购物车功能
    # 虽然token有问题,但是我们还是应该让用户 把购物车的功能实现了,等到 下单的时候 必须让它登录
    # 我们先不进行 用户的身份的验证 重写 视图的 perform_authentication 方法就可以
    # 等需要使用的时候再验证
    def perform_authentication(self, request):
        pass

    # def post(self,request):
    #     # 1. 接收数据,对数据进行校验
    #     serializer = CartSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #
    #     # 2. 获取 sku_id,count,selected
    #     sku_id = serializer.validated_data.get('sku_id')
    #     count = serializer.data.get('count')
    #     selected = serializer.data.get('selected')
    #
    #     # 3. 获取用户,根据用户信息判断登录状态
    #     try:
    #         user=request.user
    #     except Exception as e:
    #         user = None
    #
    #     # 我们要判断用户的登录状态
    #     # is_authenticated 认证用户为True
    #     # 没有认证为 False
    #     # request.user.is_authenticated
    #     if user is not None and user.is_authenticated:
    #         # 4. 登录用户redis
    #         #     4.1 连接redis
    #
    #         #     4.2 保存数据到redis中
    #         redis_conn = get_redis_connection('cart')
    #         redis_cart = redis_conn.hgetall('cart_%s' % user.id)
    #         redis_cart_select = redis_conn.smembers('cart_selected_%s' % user.id)
    #         cart = {}
    #         for sku_id, count in redis_cart.items():
    #             cart[int(sku_id)] = {
    #                 'count': int(count),
    #                 'selected': sku_id in redis_cart_select
    #             }
    #         #     4.3 返回响应
    #
    #     else:
    #         #如果是非登录用户，保存到cookie中
    #         cart_conn = request.COOKIE.get('cart')
    #     # 5. 未登录cookie
    #     #     5.1 先读取cookie数据,判断cookie中是否有购物车信息   str --> base64 -->pickle -->dict
    #     #         如果有则需要读取
    #     #         没有则不用管
    #         if cart_conn is not None:
    #             cart = pickle.loads(base64.b64decode(cart_conn.encode()))
    #         else:
    #             cart = {}
    #     #     5.2 更新购物车信息  dict
    #     #
    #     #     5.3 需要对购物车信息进行处理 dict --> pickle --> base64 -->str
    #     #
    #     #     5.4 返回响应
    #     skus = SKU.objects.filter(id__in=cart.keys())
    #     for sku in skus:
    #         sku.count = cart[sku.id]['count']
    #         sku.selected = cart[sku.id]['selected']
    #     # 序列化数据,并返回响应
    #     serializer = CartSKUSerializer(skus, many=True)
    #
    #     return Response(serializer.data)
    def post(self, request):
        """
        思路:
        #获取数据,进行校验
        #获取商品id,count和是否选中信息
        #判断用户是否为登录用户
            # 如果为登录用户则数据保存到redis中
            # 如果为非登录用户保存到cookie中
        """
        # 获取数据,进行校验
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 获取商品id,count和是否选中信息
        sku_id = serializer.data.get('sku_id')
        count = serializer.data.get('count')
        selected = serializer.data.get('selected')
        # 判断用户是否为登录用户
        try:
            user = request.user
        except Exception:
            # 验证失败,用户为登录
            user = None
        if user is not None and user.is_authenticated:
            # 如果为登录用户则数据保存到redis中
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            # 记录购物车商品数量 hash
            pl.hincrby('cart_%s' % user.id, sku_id, count)
            # 勾选
            if selected:
                pl.sadd('cart_selected_%s' % user.id, sku_id)
            pl.execute()
            # 返回响应
            return Response(serializer.data)

        else:
            # 如果为非登录用户保存到cookie中
            cart_str = request.COOKIES.get('cart')
            # 先获取cookie信息,判断是否存在购物车信息
            if cart_str is not None:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}
            # 更新购物车数量
            # 如果有相同商品，求和
            if sku_id in cart_dict:
                origin_count = cart_dict[sku_id]['count']
                count += origin_count
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 设置 cookie数据
            response = Response(serializer.data)
            cookie_cart = base64.b64encode(pickle.dumps(cart_dict)).decode()
            response.set_cookie('cart', cookie_cart)
            # 返回响应
            return response

    def get(self, request):
        """
        思路
        #判断是否为登录用户
            #登录用户,从redis中获取数据
            #非登录用户,从cookie中获取数据
        #获取所有商品的信息
        #返回响应
        """
        try:
            user = request.user
        except Exception:
            user = None
        # 判断是否为登录用户
        if user is not None and user.is_authenticated:
            # 登录用户,从redis中获取数据
            redis_conn = get_redis_connection('cart')
            redis_cart = redis_conn.hgetall('cart_%s' % user.id)
            redis_cart_select = redis_conn.smembers('cart_selected_%s' % user.id)
            cart = {}
            for sku_id, count in redis_cart.items():
                cart[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in redis_cart_select
                }

        else:
            # 非登录用户,从cookie中获取数据
            cart_str = request.COOKIES.get('cart')

            if cart_str is not None:
                cart = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart = {}

        # 获取所有商品的信息
        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            sku.count = cart[sku.id]['count']
            sku.selected = cart[sku.id]['selected']
        # 序列化数据,并返回响应
        serializer = CartSKUSerializer(skus, many=True)

        return Response(serializer.data)