from django.shortcuts import render
from rest_framework.response import Response

from goods.models import SKU
from goods.serializers import HotSKUSerializer

"""
所谓的静态化 其实就是 生成一个html 让用户去访问html

我们的首页数据是 会变化的


1. 先查询数据
2. 将查询的数据渲染到模板中
3. 写入到指定的路径

"""
# Create your views here.

from rest_framework.views import APIView

class HotSKUView(APIView):
    def get(self,request,category_id):

        # 1.前段应该传递过来一个分类id,我们应该接收这个分类id
        # 2.根据分类id查询商品数据,并对商品数据进行排序,并获取2个  [SKU,SKU,SKU]
        sku = SKU.objects.filter(category_id=category_id,is_launched=True).order_by('-sales')[:2]


        # 3.我们需要对数据进行  序列化操作(将对象转换为字典)
        serializer = HotSKUSerializer(sku,many=True)


        # 4.返回数据
        return Response(serializer.data)

