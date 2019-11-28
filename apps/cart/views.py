from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from goods.models import GoodsSKU
from django_redis import get_redis_connection


# 添加商品到购物车
# 1 请求方式,采用ajax post
# 如果涉及数据的修改(新增,删除修改)> POST
# 值涉及数据的获取 > GET
# 2 传递参数:商品id(sku_id),商品数量(count)

# /cart/add
class CartAddView(View):
    '''购物车记录添加'''

    def post(self, request):
        '''够记录添加'''

        user = request.user
        # 判断用户有没有登录
        if not user.is_authenticated():
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        # 接收数据
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        # 数据校验
        if not all([sku_id, count]):
            return JsonResponse({'res': 1, 'errmsg': '数据不完整'})
        # 校验添加的商品数量
        try:
            count = int(count)
        except Exception as e:
            # 数目出错
            return JsonResponse({'res': 2, 'errmsg': '商品数目出错'})

        # 校验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            # 商品不存在
            return JsonResponse({'res': 3, 'errmsg': '商品不存在'})

        # 业务处理:添加购物车记录
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        # 尝试获取sku_id的值 hget cart_key  属性
        cart_count = conn.hget(cart_key, sku_id)  # 如果sku_id不存在 返回none
        if cart_count:
            # 有值 > 累加购物车数目
            count += int(cart_count)

        # 校验商品的库存
        if count > sku.stock:
            return JsonResponse({'res': 4, 'errmsg': '库存不足'})
        # 设置hash中sku_id对应的值
        conn.hset(cart_key, sku_id, count)  # hset 存在就是更新.不存在就是新增

        # 计算用户购物车商品条目数
        total_count = conn.hlen(cart_key)
        # 返回应答
        return JsonResponse({'res': 5, 'total_count': total_count, 'message': '添加购物车成功'})
