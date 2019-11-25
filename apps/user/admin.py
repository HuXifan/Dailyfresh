from django.contrib import admin
from user.models import User, Address, AddressManager


# Register your models here.
class UserAdmin(admin.ModelAdmin):
    # 需要显示的字段信息
    list_display = ('id', 'username', 'date_joined')
    # 设置哪些字段可以点击进入编辑界面，默认是第一个字段
    list_display_links = ('id', 'username')
    '''每页显示条目数'''
    list_per_page = 50


class AddressAdmin(admin.ModelAdmin):
    # 需要显示的字段信息
    list_display = ('id', 'user', 'receiver', 'addr')
    # 设置哪些字段可以点击进入编辑界面，默认是第一个字段
    list_display_links = ('id', 'user')
    '''每页显示条目数'''
    list_per_page = 50


class AddressManagerAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, UserAdmin)
admin.site.register(Address, AddressAdmin)
