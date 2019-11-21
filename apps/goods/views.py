from django.shortcuts import render
from django.core.cache import cache
from django.shortcuts import render
from django.views.generic import View
# 商品类型模型类,首页轮播商品展示模型类,首页促销活动模型类
from goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner
from django_redis import get_redis_connection


# Create your views here.

# class Test(object):
#     def __init__(self):
#         self.name = 'abc'  #　给对象增加属性
#
# t = Test()
# t.age = 10
# print(t.age)


# http://127.0.0.1:8000
class IndexView(View):
    '''首页'''

    def get(self, request):
        '''查询数据，显示首页'''

        # 尝试从缓存中获取数据
        context = cache.get('index_page_data')  # 拿不到返回None
        if context is None:
            # 缓存没有数据,执行查询
            print('设置缓存')
            # 获取商品的种类信息
            types = GoodsType.objects.all()

            # 获取首页轮播商品信息
            goods_banners = IndexGoodsBanner.objects.all().order_by('index')

            # 获取首页促销活动信息, order_by 默认升序
            promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

            # 获取首页分类商品展示信息
            for type in types:  # GoodsType
                # 获取type种类首页分类商品的 图片 展示信息
                image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
                # 获取type种类首页分类商品的 文字 展示信息
                title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')

                # 动态给type对象增加属性，分别保存首页分类商品的图片展示信息和文字展示信息
                type.image_banners = image_banners
                type.title_banners = title_banners

            context = {'types': types,
                       'goods_banners': goods_banners,
                       'promotion_banners': promotion_banners,
                       }
            
            # 设置缓存 最基本的接口是 set(key, value, timeout) 和 get(key):
            cache.set('index_page_data', context, 3600)

        # 获取用户购物车中商品的数目
        user = request.user
        cart_count = 0  # 初始化为0
        # 先判断
        if user.is_authenticated():
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            # 哈希值键的名字
            cart_count = conn.hlen(cart_key)  # hlen 返回哈希集元素的数目

        # 组织模板上下文
        context.update(cart_count=cart_count)  # 添加购物车到context字典

        # 使用模板, 传context
        return render(request, 'index.html', context)
