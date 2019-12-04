from django.contrib import admin
from order.models import OrderInfo, OrderGoods


# Register your models here.


class OrderInfoAdmin(admin.ModelAdmin):
    # 需要显示的字段信息
    list_display = ('order_id', 'user', 'addr', 'pay_method', 'total_count', 'total_price', 'trade_no')
    # 设置哪些字段可以点击进入编辑界面，默认是第一个字段
    list_display_links = ('order_id', 'user')
    '''每页显示条目数'''
    list_per_page = 50


class OrderGoodsAdmin(admin.ModelAdmin):
    # 需要显示的字段信息
    list_display = ('order', 'sku', 'sku_name', 'count', 'price')
    # 设置哪些字段可以点击进入编辑界面，默认是第一个字段
    list_display_links = ('order', 'sku', 'sku_name')

    def sku_name(self, obj):
        return '%s' % obj.sku.name  # ☆

    sku_name.short_description = '商品名'
    '''每页显示条目数'''
    list_per_page = 50


admin.site.register(OrderInfo, OrderInfoAdmin)
admin.site.register(OrderGoods, OrderGoodsAdmin)
