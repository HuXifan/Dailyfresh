from django.shortcuts import render
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.paginator import Paginator
# 商品类型模型类,首页轮播商品展示模型类,首页促销活动模型类
from goods.models import GoodsType, GoodsSKU, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner
from order.models import OrderGoods
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


# /goods/商品id
class DetailView(View):
    '''详情页'''

    def get(self, request, goods_id):
        # 显示详情页
        try:
            sku = GoodsSKU.objects.get(id=goods_id)
        except GoodsSKU.DoesNotExist:
            # 商品id不存在
            return render(reverse('goods:index'))

        # 获取商品分类信息
        types = GoodsType.objects.all()
        # 获取商品评论信息
        sku_orders = OrderGoods.objects.filter(sku=sku).exclude(comment='')  # sku等于查到的sku,exclude()排除满足条件的查询集

        # 获取新品信息  # base_model 通用都有穿件和修改时间 根据时间 最新的就是最近的
        new_skus = GoodsSKU.objects.filter(type=sku.type).order_by('-create_time')[:2]  # 新品取两个

        # 获取同一SPU的其他规格的商品
        same_spu_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=goods_id)  # 排除id相同的商品

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

            # 　添加用户的历史浏览记录
            conn = get_redis_connection('default')
            history_key = 'history_%d' % user.id
            # 移出列表中的goods_id
            conn.lrem(history_key, 0, goods_id)
            # 插入goods_id到列表最左侧
            conn.lpush(history_key, goods_id)
            # 只保存用户最新浏览的五条纪录
            conn.ltrim(history_key, 0, 4)

        # 组织模板上下文
        context = {
            'sku': sku,
            'types': types,
            'sku_orders': sku_orders,
            'new_skus': new_skus,
            'same_spu_skus': same_spu_skus,
            'cart_count': cart_count
        }
        # 使用模板
        return render(request, 'detail.html', context)


# 　种类id,页码,排序方式
# 　/list/种类id/页码/排序方式
# 　/list/种类id/页码?sort=排序方式
class ListView(View):
    '''列表页'''

    def get(self, request, type_id, page):
        # 显示列表页
        # 获取种类信息
        try:
            type = GoodsType.objects.get(id=type_id)
        except GoodsType.DoesNotExist:
            # 种类不存在
            return redirect(reverse('goods:index'))

        # # 获取商品的分类信息
        types = GoodsType.objects.all()
        # print(type)
        # 获取排序方式
        sort = request.GET.get('sort')
        # sort = default/price/hot # 按照默认/价格/人气(销量)排序
        if sort == 'price':
            skus = GoodsSKU.objects.filter(type=type).order_by('price')  # 升序
        elif sort == 'hot':
            skus = GoodsSKU.objects.filter(type=type).order_by('-sales')
        else:
            sort = 'default'
            skus = GoodsSKU.objects.filter(type=type).order_by('-id')

        # 对数据进行分页
        paginator = Paginator(skus,1)

        # 获取第page页的内容
        try:
            page = int(page)
        except Exception as e:
            page = 1  # 出错就显示第一页

        if page > paginator.num_pages:
            page = 1

        # 获取第page页的Page实例对象
        skus_page = paginator.page(page)

        # 获取新品信息  # base_model 通用都有穿件和修改时间 根据时间 最新的就是最近的
        new_skus = GoodsSKU.objects.filter(type=type).order_by('-create_time')[:2]  # 新品取两个

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
        context = {
            'type': type,
            'types': types,
            'skus_page': skus_page,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'sort': sort
        }
        # 使用模板
        return render(request, 'list.html', context)
