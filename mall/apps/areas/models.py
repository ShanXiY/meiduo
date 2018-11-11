from django.db import models

class Area(models.Model):
    """
    行政区划
    """
    name = models.CharField(max_length=20, verbose_name='名称')
    #related_name='' 可以修改关联模型属性的默认名字，默认名字是 关联模型类名小写_set
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs', null=True, blank=True, verbose_name='上级行政区划')

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '行政区划'
        verbose_name_plural = '行政区划'

    def __str__(self):
        return self.name


#  id           name        parent_id

# 10000         河北省         NULL



# 10200         保定市             10000




# 10210         定兴县          10200
# 10220         涿州市          10200