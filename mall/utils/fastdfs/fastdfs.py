from mall import settings
from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client

# 4.使用装饰器
# django.utils.deconstruct.deconstructible类装饰器
from django.utils.deconstruct import deconstructible

#1.您的自定义存储系统必须是以下子类 django.core.files.storage.Storage：
@deconstructible
class MyStorage(Storage):
    #2.Django必须能够在没有任何参数的情况下实例化您的存储系统。
    # 这意味着任何设置都应该来自django.conf.settings
    # def __init__(self, conf_path=None,ip=None,name):  这样定义的错误的
    #                                               因为我们在初始化的时候要传参数
    def __init__(self,conf_path=None,ip=None):
        pass

        # 3.您的存储类必须实现_open()和_save() 方法以及适用于您的存储类的任何其他方法

        # 打开图片
        # 因为我们是通过 http的方式来获取图片的,所有需要在此方法中写任何代码
    def _open(self, name, mode='rb'):
        pass

    #保存
    def _save(self, name, content, max_length=None):

        # 1.创建客户端的实例对象
        # 配置文件路径
        # client = Fdfs_client('utils/fastdfs/client.conf')
        # client = Fdfs_client(settings.FDFS_CLIENT_CONF)
        client = Fdfs_client(self.conf_path)

        # 2.上传图片

        # name 只是图片的名字 不是绝对路径
        # content 内容, 图片的内容,我们需要通过 read() 方法来读取图片的资源
        # read的读取的资源是二进制
        data = content.read()

        # client.upload_by_filename()  需要知道文件的绝对路径

        # upload_by_buffer 上传二进制

        # upload_by_buffer 会返回上传结果

        result = client.upload_by_buffer(data)

        # 3.判断上传结果,获取 file_id
        if result.get('Status') == 'Upload successed.':
            # 上传成功了
            file_id = result.get('Remote file_id')
            # 我们需要将 file_id  返回给系统,系统需要使用这个 file_id
            return file_id
        else:
            raise Exception('上传失败')
        # exists 存在
        # 判断图片是否存在
        # 返回一个false就可以,因为fastdfs 可以处理重名的请求
        # 返回 False的意思就是说: 你尽管上传,不会出现覆盖的情况

    def exists(self, name):
        return False

    def url(self, name):

        # 默认这个 url 是返回name的值
        # name的值其实就是 file_id 的值

        # 我们访问图片的时候 真实的路径是 http://ip:port/ + file_id
        # 所以我们返回url的时候 就直接 把拼接好的url返回
        # return 'http://192.168.229.133:8888/' + name
        # return settings.FDFS_URL + name

        return self.ip + name

