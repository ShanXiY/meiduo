from django.shortcuts import render

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

class PlaceOrderView(APIView):
    def get(self,request):
        # 1. 登录用户才可以访问
        # 2. 连接redis,获取redis中的数据(选中的商品数据)
        #     hash        sku_id:count
        #     set         {sku_id,sku_id}
        #     因为我们要的是 选中商品的信息
        #
        #     最终得到的数据 只有 sku_id 和 count
        # 3. 根据id  [sku_id,sku_id,sku_id] 获取商品的信息信息 [SKU,SKU,SKU]
        #
        # 4. 我们需要对 对象列表转换成字典列表
        #
        # 5. 返回响应

        pass
