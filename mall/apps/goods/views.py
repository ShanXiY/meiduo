from django.shortcuts import render
from rest_framework.response import Response

from goods.models import SKU
from goods.serializers import HotSKUSerializer
from utils.pagination import StandardResultsSetPagination

"""
所谓的静态化 其实就是 生成一个html 让用户去访问html

我们的首页数据是 会变化的


1. 先查询数据
2. 将查询的数据渲染到模板中
3. 写入到指定的路径

"""
# Create your views here.

"""
获取商品列表 推荐信息


# 1.前段应该传递过来一个分类id,我们应该接收这个分类id
# 2.根据分类id查询商品数据,并对商品数据进行排序,并获取2个  [SKU,SKU,SKU]
# 3.我们需要对数据进行  序列化操作(将对象转换为字典)
# 4.返回数据

GET     goods/categories/cat_id/hotskus/



"""


from rest_framework.views import APIView

# class HotSKUView(APIView):
#     def get(self,request,category_id):
#
#         # 1.前段应该传递过来一个分类id,我们应该接收这个分类id
#         # 2.根据分类id查询商品数据,并对商品数据进行排序,并获取2个  [SKU,SKU,SKU]
#         sku = SKU.objects.filter(category_id=category_id,is_launched=True).order_by('-sales')[:2]
#
#
#         # 3.我们需要对数据进行  序列化操作(将对象转换为字典)
#         serializer = HotSKUSerializer(sku,many=True)
#
#
#         # 4.返回数据
#         return Response(serializer.data)

from rest_framework.generics import ListAPIView

class HotSKUView(ListAPIView):

    serializer_class = HotSKUSerializer

    def get_queryset(self):
        category_id = self.kwargs['category_id']

        return SKU.objects.filter(category_id=category_id,is_launched=True).order_by('-sales')[:2]

"""
列表页面数据获取


1. 先实现返回所有分类数据
2. 再实现排序
3. 最后实现 分页


GET     /goods/categories/(?P<category_id>\d+)/skus/?ordering=-price&page_size=2&page=3
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter


class SKUListAPIView(ListAPIView):

    #排序
    filter_backends = [OrderingFilter]

    #设置拍序字段
    ordering_fields = ['create_time','price','sales']

    #分页类
    # pagination_class = StandardResultsSetPagination

    serializer_class = HotSKUSerializer

    def get_queryset(self):

        category_id = self.kwargs['category_id']

        return SKU.objects.filter(category_id=category_id, is_launched=True)

