from django.shortcuts import render
from rest_framework.response import Response

from goods.models import SKU
from orders.serializers import OrderPlacesSerializer

"""
 当用户点击结算的时候,必须让用户登录
 如果是登录用户,我们会跳转到结算页面. 页面需要获取 用户的购物车信息(选中的商品信息)


1. 登录用户才可以访问
2. 连接redis,获取redis中的数据(选中的商品数据)
    hash        sku_id:count
    set         {sku_id,sku_id}
    因为我们要的是 选中商品的信息

    最终得到的数据 只有 sku_id 和 count
3. 根据id  [sku_id,sku_id,sku_id] 获取商品的信息信息 [SKU,SKU,SKU]

4. 我们需要对 对象列表转换成字典列表

5. 返回响应

GET     /orders/places/



"""


# Create your views here.

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_redis import get_redis_connection
class PlaceOrderView(APIView):

    # 1. 登录用户才可以访问
    permission_classes = [IsAuthenticated]

    def get(self,request):
        user = request.user

        # 2. 连接redis,获取redis中的数据(选中的商品数据)
        redis_conn = get_redis_connection('cart')
        #     hash        sku_id:count
        sku_count = redis_conn.hgetall('cart_%s'%user.id)
        #     set         {sku_id,sku_id}
        selected_ids = redis_conn.smembers('cart_selected_%s'%user.id)
        #     因为我们要的是 选中商品的信息
        #       对选中的商品进行遍历，来组织新的数据
        selected_cart = {}

        for sku_id in selected_ids:
            selected_cart[int(sku_id)] = int(sku_count[sku_id])

        #     最终得到的数据 只有 sku_id 和 count
        # 3. 根据id  [sku_id,sku_id,sku_id] 获取商品的信息信息 [SKU,SKU,SKU]
        skus = SKU.objects.filter(pk__in=selected_cart.keys())

        for sku in skus:
            #给实例对象动态添加属性
            sku.count = selected_cart[sku.id]

        # 4. 我们需要对 对象列表转换成字典列表
        freight = 10
        serializer = OrderPlacesSerializer({'freight':freight,
                                            'skus':skus})

        # 5. 返回响应

        return Response(serializer.data)

"""

 当用户点击提交按钮的时候 ,前端应该将 用户信息(header jwt-token),收货地址,支付方式传递过来

 1. 接收数据
 2. 校验
 3. 保存数据
 4. 返回响应

 POST   /orders/
"""

from rest_framework.mixins import CreateModelMixin
from rest_framework.generics import CreateAPIView
from .serializers import OrderPlacesSerializer

class OrderCreateAPIView(CreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = OrderPlacesSerializer
