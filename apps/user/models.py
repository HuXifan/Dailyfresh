from django.db import models
from django.contrib.auth.models import AbstractUser
from db.base_model import BaseModel


class User(AbstractUser, BaseModel):
    '''用户模型类'''

    class Meta:
        db_table = 'df_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class AddressManager(models.Manager):
    '''# 模型管理器对象,应用方法123
    self.model:获取self对象所在的模型类
    '''

    # 1 改变原有的查询结果集:all(), 进行过滤
    # 2 封装方法:用户操作的模型类对应的数据表.(增删改查)
    def get_default_address(self, user):
        """获取用户默认收货地址"""
        try:
            address = self.model.objects.get(user=user, is_default=True)  # models.Manager 对象
        except self.model.DoesNotExist:
            # 　不存在默认收货地址，赋值None
            address = None
        return address


class Address(BaseModel):
    '''地址模型类'''
    user = models.ForeignKey('User', verbose_name='所属账户')
    receiver = models.CharField(max_length=20, verbose_name='收件人')
    addr = models.CharField(max_length=256, verbose_name='收件地址')
    zip_code = models.CharField(max_length=6, null=True, verbose_name='邮政编码')
    phone = models.CharField(max_length=11, verbose_name='联系电话')
    is_default = models.BooleanField(default=False, verbose_name='是否默认')

    objects = AddressManager()  # 自定义一个模型管理器对象

    class Meta:
        db_table = 'df_address'
        verbose_name = '地址'
        verbose_name_plural = verbose_name
