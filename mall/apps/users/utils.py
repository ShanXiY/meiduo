from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from mall import settings

def generic_active_url(user_id,email):
    #token中应该含有用户信息

    #1.创建序列化器
    serializer = Serializer(settings.SECRET_KEY,3600)

    #2.组织数据
    data = {
        'id':user_id,
        'email':email
    }

    #3.对数据进行处理
    token = serializer.dumps(data)

    #4.返回url
    return 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token.decode()