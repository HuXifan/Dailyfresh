from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.views.generic import View
from goods.models import GoodsSKU
from user.models import Address
from utils.mixin import LoginRequiredMixin
from django_redis import get_redis_connection
from django.http import JsonResponse


# /order/place
class OrderPlaceView(LoginRequiredMixin, View):
    '''提交订单页面'''

    def post(self, request):
        # 提交订单页面显示
        user = request.user

        # 获取参数sku-ids
        sku_ids = request.POST.getlist('sku_ids')

        # 校验参数
        if not sku_ids:
            # 跳转到购物车页面
            return redirect(reverse('cart:show'))

        # 取得连接
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id

        skus = []
        total_count = 0  # 保存商品总件数总价格
        total_price = 0
        # 遍历sku_ids 获取用户索要购买的商品的信息
        for sku_id in sku_ids:
            # 根据商品的id获取商品的信息
            sku = GoodsSKU.objects.get(id=sku_id)
            # 获取用户索要购买商品数量
            count = conn.hget(cart_key, sku_id)
            # 计算商品小计
            amount = sku.price * int(count)

            # 动态给sku增加属性,保存 购买商品的数量,购买商品的小计
            sku.count = count
            sku.amount = amount
            # 追加
            skus.append(sku)
            # 累计计算商品的总件数和总价格
            total_price += amount
            total_count += int(count)
        # 运费：实际开发的时候，属于的子系统
        transit_price = 10  # 写死

        # 实付款
        total_pay = total_price + transit_price

        # 获取用户的收件地址
        addrs = Address.objects.filter(user=user)

        # 组织上下文
        context = {
            'skus': skus,
            'total_price': total_price,
            'total_count': total_count,
            'transit_price': transit_price,
            'total_pay': total_pay,
            'addrs': addrs,
            'sku_ids': sku_ids
        }
        # 使用模板
        return render(request, 'place_order.html', context)
