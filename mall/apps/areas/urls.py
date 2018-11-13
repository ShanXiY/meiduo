from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'infos',views.AreaViewSet,base_name='')

urlpatterns = [

]

#添加省市区信息查询路由
urlpatterns += router.urls