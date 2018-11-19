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

from orders.models import OrderInfo
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

        return order


