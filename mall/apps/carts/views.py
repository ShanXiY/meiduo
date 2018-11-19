import base64
import pickle

from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response

from carts.serializers import CartSerializer, CartSKUSerializer, CartDeleteSerializer
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

            # # redis_conn.hset('cart_%s'%user.id,sku_id,count)
            # redis_conn.hincrby('cart_%s' % user.id, sku_id, count)
            #
            # # set
            # redis_conn.sadd('cart_selected_%s' % user.id, sku_id)

            #创建管道
            pl = redis_conn.pipeline()
            # 记录购物车商品数量 hash
            pl.hincrby('cart_%s' % user.id, sku_id, count)
            # 勾选
            if selected:
                pl.sadd('cart_selected_%s' % user.id, sku_id)

            #管道执行命令
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
                # cart[sku_id] = {
                #     'count': count,
                #     'selected': sku_id in redis_cart_select
                # }
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

    """
    修改购物车的业务逻辑

    用户在修改数据的时候,前端应该将 修改之后的  sku_id,count,selected 发送给后端
    额外强调一下 ,我们的count是用户 最终的值

    1. 接收数据,并进行数据的校验
    2. 获取sku_id,count,selected的值
    3. 获取用户信息,并进行判断
    4. 登录用户redis
        4.1 连接redis
        4.2 更新数据
        4.3 返回数据 (一定要将 最终的商品数据 返回回去)
    5. 未登录用户 cookie
        5.1 读取cookie,并判断数据是否存在
        5.2 更新数据 dict
        5.3 对字典进行处理
        5.4 返回响应(一定要将 最终的商品数据 返回回去)


    """
    def put(self,request):
        #1.接收数据，进行数据的校验
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        #2.获取sku_id,count,selected 的值
        sku_id = serializer.data.get('sku_id')
        count = serializer.data.get('count')
        selected = serializer.data.get('selected')

        #3.获取用户信息，进行判断
        try:
            user = request.user
        except Exception:
            user = None
        if user is not None and user.is_authenticated:
            #4.登录用户redis
            #4.1连接redis
            redis_conn = get_redis_connection('cart')
            #4.2更新数据
            redis_conn.hset('cart_%s'%user.id,sku_id,count)
            #set
            #选中状态
            if selected:
                redis_conn.sadd('cart_selected_%s'%user.id,sku_id)
            else:
                #未选中
                redis_conn.srem('cart_%s'%user.id,sku_id)
            #4.3返回数据(要将最终的商品数据返回回去)
            return Response(serializer.data)

        else:
            #5.未登录用户 cookie
            #5.1读取cookie，并判断数据是否存在
            cookie_str = request.COOKIES.get('cart')
            if cookie_str is not None:
                #读取数据
                cart = pickle.loads(base64.b64decode(cookie_str))
            else:
                cart = {}
            #5.2更新数据
            if sku_id in cart:
                cart[sku_id] = {
                    'count':count,
                    'selected':selected
                }
            #5.3对字典进行处理
            new_cookie = base64.b64encode(pickle.dumps(cart)).decode()
            #5.4返回响应
            response = Response(serializer.data)
            response.set_cookie('cart',new_cookie)
            return response

    """
    删除功能
    用户点击删除按钮的时候,前端应该发送一个 ajax请求,请求中包含 sku_id        jwt

    1. 接收参数,并对参数进行校验
    2. 获取用户信息,并根据用户信息进行判断
    3. 登录用户redis
        3.1 连接redis
        3.2 删除数据 hash,set
        3.3 返回响应
    4. 未登录用户 cookie
        4.1 获取cookie数据并进行判断
        4.2 删除数据
        4.3 dict 对购物车数据进行处理
        4.4 返回响应

    """
    def delete(self,request):
        #1.接收参数，对参数进行校验
        serializer = CartDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sku_id = serializer.data.get('sku_id')
        #2.获取用户信息，根据用户信息进行判断
        try:
            user = request.user
        except Exception:
            user = None
        if user is not None and user.is_authenticated:
            # 3. 登录用户redis
            #     3.1 连接redis
            redis_conn = get_redis_connection('cart')
            #     3.2 删除数据 hash,set
            redis_conn.hdel('cart_%s'%user.id,sku_id)
            redis_conn.srem('cart_selected_%s'%user.id,sku_id)
            #     3.3 返回响应
            return Response(serializer.data)
        else:
            # 4. 未登录用户 cookie
            #     4.1 获取cookie数据并进行判断
            cookie_str = request.COOKIES.get('cart')
            if cookie_str is not None:
                cart = pickle.loads(base64.b64decode(cookie_str))
            else:
                cart = {}
            #     4.2 删除数据
            if sku_id is cart:
                del cart[sku_id]

            #     4.3 dict 对购物车数据进行处理
            new_cookie = base64.b64encode(pickle.dumps(cart)).decode()
            #     4.4 返回响应
            response = Response(serializer.data)

            response.set_cookie('cart',new_cookie)

            return response
