"""

在登录的时候 ,将cookie数据合并到redis中


cookie: {sku_id:{count:xxx,selected:xxxx}}

redis:  hash:  {sku_id:count}
        set:    {sku_id}

把抽象的问题具体化

cookie:
    {1:{count:20,selected:True},    3:{count:10,selected:False}}

Redis
    hash:    {2:100,3:50}
    set:    {2}

########################################################
合并之后的数据
    hash    {2:100,3:10,1:20}
    set     {2,1}

# 分析具体情况
    redis的数据 原封不动的保留
    cookie数据要合并到 redis的时候 ,我们就来分析 cookie数据 就三个: sku_id,count,selected

    1. cookie中 含有商品id,redis中没有, 这个时候 将cookie的id添加进来,数量以cookie为主
    2. cookie中 含有商品id,redis也有, 这个时候 数量怎么办, 以cookie为主



代码是具体化的事物转换为抽象的东西

# 1.获取cookie数据
# 2.获取redis数据
# 3.合并
# 4.将更新的数据 写入到redis中
# 5.删除cookie



"""

import base64
import pickle
from django_redis import get_redis_connection

def merge_cookie_to_redis(request,user,response):

    # 1.获取cookie数据
    cookie_str = request.COOKIES.get('cart')
    if cookie_str is not None:
        #说明有
        # {1:{count:5,selected:True}}
        cookie_cart = pickle.loads(base64.b64decode(cookie_str))

        # 2.获取redis数据
        redis_conn = get_redis_connection('cart')
        # hash
        # request.user
        hash_cart = redis_conn.hgetall('cart_%s'%user.id)

        # {b'1':b'5',b'3':b'10'}
        # 因为redis的数据是bytes类型,我们最好对数据进行一个处理
        cart = {}
        for sku_id,count in hash_cart.items():
            cart[int(sku_id)] = int(count)

        # 3.合并,对cookie数据进行遍历
        #{2:{count:20,selected:True}}

        # 我们用一个空的列表 来接收选中的id,然后再把选中的id添加到 set中就可以了
        selected_ids = []

        for sku_id,count_selected_dict in cookie_cart.items():

            # 判断sku_id 是否在 cart中
            # if sku_id in cart:
            #     cart[sku_id]=count_selected_dict['count']
            # else:
            #     cart[sku_id]=count_selected_dict['count']
            #因为数量是以 cookie为主,所以 数量就获取cookie
            cart[sku_id] = count_selected_dict['count']

            #选中的状态
            if count_selected_dict['selected']:
                selected_ids.append(sku_id)


        # 4.将更新的数据 写入到redis中

        # cart 是最新的购物车数据,直接 写入到redis中就可以了
        redis_conn.hmset('cart_%s'%user.id, cart)

        # selected_ids 是新增的选中的商品的id 添加到set中就可以了
        redis_conn.sadd('cart_selected_%s'%user.id,*selected_ids)

        # 5.删除cookie
        response.delete_cookie('cart')


        return response


    return response