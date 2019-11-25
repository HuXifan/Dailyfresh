from django.contrib import admin
from django.core.cache import cache
from goods.models import Goods, GoodsType, GoodsSKU, IndexPromotionBanner, IndexGoodsBanner, IndexTypeGoodsBanner


# Register your models here.
class BaseModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        # 新增或更新表中的数据时调用
        super().save_model(request, obj, form, change)

        # 发出任务,让celery worker冲新生成静态页面
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()

        # 清除首页缓存
        cache.delete('index_page_data')

    def delete_model(self, request, obj):
        # 删除任务表数据时调用
        super().delete_model(request, obj)
        # 发出任务 celery worker 重新生成首页静态页面
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()
        # 清除首页缓存
        cache.delete('index_page_data')


# 商品SPU模型类
class GoodsAdmin(BaseModelAdmin):
    # 需要显示的字段信息
    list_display = ('id', 'name', 'detail')
    # 设置哪些字段可以点击进入编辑界面，默认是第一个字段
    list_display_links = ('id', 'name')
    '''每页显示条目数'''
    list_per_page = 50


# 商品类型
class GoodsTypeAdmin(BaseModelAdmin):
    # 需要显示的字段信息
    list_display = ('id', 'name', 'logo')
    # 设置哪些字段可以点击进入编辑界面，默认是第一个字段
    list_display_links = ('id', 'name')
    '''每页显示条目数'''
    list_per_page = 20


# 商品SKU模型类
class GoodsSKUAdmin(BaseModelAdmin):
    # 需要显示的字段信息
    list_display = ('id', 'type', 'name', 'status')
    # 设置哪些字段可以点击进入编辑界面，默认是第一个字段
    list_display_links = ('id', 'name')
    '''每页显示条目数'''
    list_per_page = 20


# 首页轮播商品
class IndexGoodsBannerAdmin(BaseModelAdmin):
    # 需要显示的字段信息
    list_display = ('id', 'sku', 'sku_name', 'index')
    # 设置哪些字段可以点击进入编辑界面，默认是第一个字段
    list_display_links = ('id', 'sku')
    '''每页显示条目数'''
    list_per_page = 10

    def sku_name(self, obj):
        return '%s' % obj.sku.name  # ☆

    sku_name.short_description = '商品名'


# 主页分类展示商品
class IndexTypeGoodsBannerAdmin(BaseModelAdmin):
    # 需要显示的字段信息
    list_display = ('id', 'sku_name', 'type', 'display_type')
    # 设置哪些字段可以点击进入编辑界面，默认是第一个字段
    list_display_links = ('id', 'sku_name')
    '''每页显示条目数'''
    list_per_page = 20

    def sku_name(self, obj):
        return '%s' % obj.sku.name  # ☆

    sku_name.short_description = '商品名'


# 首页促销活动模型类
class IndexPromotionBannerAdmin(BaseModelAdmin):
    # 需要显示的字段信息
    list_display = ('id', 'name', 'index')
    # 设置哪些字段可以点击进入编辑界面，默认是第一个字段
    list_display_links = ('id', 'name')
    '''每页显示条目数'''
    list_per_page = 20


admin.site.register(GoodsType, GoodsTypeAdmin)
admin.site.register(Goods, GoodsAdmin)
admin.site.register(GoodsSKU, GoodsSKUAdmin)
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
admin.site.register(IndexTypeGoodsBanner, IndexTypeGoodsBannerAdmin)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)
