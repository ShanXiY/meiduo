"""
我们的任务，worker，broker都需要Celery去协调，所以我们需要创建一个Celery对象
"""

from celery import Celery

#celery也是需要用到django项目中的配置信息的

#进行django允许配置
#为celery使用django配置文件进行设置
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'mall.settings'
#以上配置加载到app创建前边

#1.创建celery对象
#第一个参数：main一般以celery的文件夹为名字，不要重复
app = Celery('celery_tasks')

#2.设置broker
#config_from_object 设置配置文件的路径
app.config_from_object('celery_tasks.config')

#3.celery 可以自动检测任务
#autodiscover_tasks第一个参数就是列表
#列表中的元素是任务包的路径
#路径是从celery_tasks开始
app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.email'])

#worker是通过指令来执行的
#celery -A celery 实例对象的文件路径 worker -l info

#这个指令需要在虚拟环境中执行
#celery -A celery_tasks worker -l info