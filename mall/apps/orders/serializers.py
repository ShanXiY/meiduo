from django.contrib.gis.geos import point
from django.db import transaction
from rest_framework import serializers

from goods.models import SKU


class CartSKUSerializer(serializers.ModelSerializer):
    """
    购物车商品数据序列化器
    """
    count = serializers.IntegerField(label='数量')

    class Meta:
        model = SKU
        fields = ('id', 'name', 'default_image_url', 'price', 'count')


class OrderPlacesSerializer(serializers.Serializer):
    """
    订单结算数据序列化器
    """
    freight = serializers.DecimalField(label='运费', max_digits=10, decimal_places=2)
    skus = CartSKUSerializer(many=True)

from orders.models import OrderInfo, OrderGoods
from django_redis import get_redis_connection
class OrderCommitSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderInfo
        fields = ('order_id', 'address', 'pay_method')
        read_only_fields = ('order_id',)
        extra_kwargs = {
            'address': {
                'write_only': True,
                'required': True,
            },
            'pay_method': {
                'write_only': True,
                'required': True
            }
        }

    def create(self, validated_data):
        """
        大的思路是: 先生成订单,再保存订单商品
        因为 订单商品 需要 订单id

        生成订单
        # 1.获取user信息
        # 2.获取地址信息
        # 3.我们生成一个订单号
        # 4.运费,价格,数量
        # 5.支付方式
        # 6. 状态

           redis
                hash  sku_id:count
                set     sku_id,sku_id 选中的

        # 7. 连接redis,获取redis数据
        # 8. 获取选中商品的信息  {sku_id:count}
        # 9. 根据id 获取商品的信息  [SKU,SKU,SKu]
        # 10.我们需要对 商品信息进行遍历
        #     11. 我们需要修改商品的库存和销量
        #     12. 我们需要累计 总的商品价格和数量
        #     13. 保存商品

        保存订单


        """
        # 1.获取user信息
        user = self.context['request'].user

        # 2.获取地址信息
        address = validated_data.get('address')

        # 3.我们生成一个订单号
        from django.utils import timezone
        order_id = timezone.now().strftime('%Y%m%d%H%M%S%f') + ('%06d'%user.id)

        # 4.运费,价格,数量
        total_count = 0

        #Decimal是一个货币类型
        from decimal import Decimal

        total_amount = Decimal('0')

        freight = Decimal('10.00')

        # 5.支付方式
        pay_method = validated_data.get('pay_method')

        # 6. 状态 会因为 支付方式而不同
        if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']:
            #货到付款
            status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        else:
            #支付宝
            status = OrderInfo.ORDER_STATUS_ENUM['UNPAID']

        #我们应该在这里开始进行事务
        with transaction.atomic():

            order = OrderInfo.objects.create(
                order_id=order_id,
                user=user,
                address=address,
                total_amount=total_amount,
                total_count=total_count,
                freight=freight,
                pay_method=pay_method,
                status=status
            )

            # 7. 连接redis,获取redis数据
            redis_conn = get_redis_connection('cart')

            #hash
            sku_id_count =redis_conn.hgetall('cart_%s'%user.id)

            #set
            selected_ids = redis_conn.smsmbers('cart_selected_%s'%user.id)
            # 8. 获取选中商品的信息  {sku_id:count}
            selected_cart = {}
            for sku_id in selected_ids:
                selected_cart[int(sku_id)] = int(sku_id_count[sku_id])

            # 9. 根据id 获取商品的信息  [SKU,SKU,SKu]
            skus = SKU.objects.filter(pk__in=selected_cart.keys())

            # 10.我们需要对 商品信息进行遍历
            for sku in skus:
                #获取数量
                count = selected_cart[sku.id]

                #判断售卖数量和库存
                if count > sku.stock:
                    raise serializers.ValidationError('库存不足')

            #     11. 我们需要修改商品的库存和销量
                import time
                time.sleep(5)

            #     sku.stock -= count
            #     sku.sales += count
                #乐观锁，并不是真的锁
                #他先查询(记录)库存，等修改的时候再查询一次库存

                #①先记录库存
                old_stock = sku.stock

                #②最终肯定要更新数据，所以先把最新的数据准备好
                new_stock = sku.stock - count
                new_sales = sku.stock + count

                #③修改数据时，再查询一次
                result = SKU.objects.filter(pk=sku.id,stock=old_stock).update(stock=new_stock,sales=new_sales)

                if result == 0:
                    raise serializers.ValidationError('下单失败')

            #     12. 我们需要累计 总的商品价格和数量
                order.total_count += count
                order.total_amount += (sku.price*count)

            #     13. 保存商品
                OrderGoods.objedcts.create(
                    order=order,
                    sku=sku,
                    count=count,
                    price=sku.price
                )
            #对商品的数量和总价格进行了累加，所以要保存
            order.save()

            transaction.savepoint_commit(point)

        return order


