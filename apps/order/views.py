from datetime import datetime
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.views.generic import View
from goods.models import GoodsSKU
from order.models import OrderInfo, OrderGoods
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
        sku_ids = ','.join(sku_ids)  # [1,25] -> 1,25
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

#
# # /order/commit
# class OrderCommitView(View):
#     '''创建订单视图'''
#     '''前端传递的参数:地址id,支付方式pay_method,用户要购买的商品id:sku-ids'''
#
#     def post(self, request):
#         # 订单创建
#         # 判断用户用户是否登录
#         user = request.user
#         if not user.is_authenticated():
#             # 用户未登录
#             return JsonResponse({'res': 0, 'errmsg': '用户未登录'})
#         # 接收参数
#         addr_id = request.POST.get('addr_id')
#         pay_method = request.POST.get('pay_method')
#         sku_ids = request.POST.get('sku_ids')
#
#         # 校验参数
#         # 1 数据完整性
#         if not all([addr_id, sku_ids, sku_ids]):
#             return JsonResponse({'res': 1, 'errmsg': '参数不完整'})
#
#         # 校验支付方式
#         if pay_method not in OrderInfo.PAY_METHODS.keys():
#             # 不在PAY_METHODS的字典里
#             return JsonResponse({'res': 2, 'errmsg': '非法的支付方式'})
#         # 校验地址
#         try:
#             addr = Address.objects.get(id=addr_id)
#         except Address.DoesNotExist:
#             return JsonResponse({'res': 3, 'errmsg': '地址非法'})
#
#         # 创建订单 核心业务
#
#         # 组织参数 订单id:year-mon-day-hour-min-sec
#         order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(user.id)
#         # 运费写死
#         transit_price = 10
#         # 总数目总金额,设置初始值0
#         total_count = 0
#         total_price = 0
#
#         # todo: 向df_order_info 添加一条记录
#         order = OrderInfo.objects.create(order_id=order_id,
#                                          user=user, addr=addr,
#                                          pay_method=pay_method,
#                                          total_count=total_count,
#                                          total_price=total_price,
#                                          transit_price=transit_price)
#         # todo 用户订单有几个商品就需要添加几条记录
#         sku_ids = sku_ids.split(',')  # 切字符串为列表
#         # 取得连接
#         conn = get_redis_connection('default')
#         cart_key = 'cart_%d' % user.id
#
#         for sku_id in sku_ids:
#             # 获取商品信息
#             try:
#                 sku = GoodsSKU.objects.get(id=sku_id)
#             except:
#                 return JsonResponse({'res': 4, 'errmsg': '商品不存在'})
#
#             # 从redis中获取用户索要购买的商品数量
#             count = conn.hget(cart_key, sku_id)
#
#             # 向df_order＿info添加几条记录,遍历,有几条就加几条记录
#             OrderGoods.objects.create(order=order,
#                                       sku=sku,
#                                       count=count,
#                                       price=sku.price)
#             # todo 更新商品的库存和销量
#             sku.stock -= int(count)
#             sku.sales += int(count)
#             sku.save()
#
#             # 累加计算订单商品的总数目 总价格
#             amount = sku.price * int(count)
#             total_count += int(count)
#             total_price += amount
#
#         # 出了循环外 更新订单信息表中的商品总数量和总价格
#         order.total_count = total_count
#         order.total_price = total_price
#         order.save()
#         # 清除购物车里用户购买过的商品记录
#         conn.hdel(cart_key, *sku_ids)
#
#         # 返回应答
#         return JsonResponse({'res': 5, 'errmsg': '创建订单成功'})


class OrderCommitView(View):
    '''订单创建'''
    def post(self, request):
        '''订单创建'''
        # 判断用户是否登录
        user = request.user
        if not user.is_authenticated():
            # 用户未登录
            return JsonResponse({'res':0, 'errmsg':'用户未登录'})

        # 接收参数
        addr_id = request.POST.get('addr_id')
        pay_method = request.POST.get('pay_method')
        sku_ids = request.POST.get('sku_ids') # 1,3

        # 校验参数
        if not all([addr_id, pay_method, sku_ids]):
            return JsonResponse({'res':1, 'errmsg':'参数不完整'})

        # 校验支付方式
        if pay_method not in OrderInfo.PAY_METHODS.keys():
            return JsonResponse({'res':2, 'errmsg':'非法的支付方式'})

        # 校验地址
        try:
            addr = Address.objects.get(id=addr_id)
        except Address.DoesNotExist:
            # 地址不存在
            return JsonResponse({'res':3, 'errmsg':'地址非法'})

        # todo: 创建订单核心业务

        # 组织参数
        # 订单id: 20171122181630+用户id
        order_id = datetime.now().strftime('%Y%m%d%H%M%S')+str(user.id)

        # 运费
        transit_price = 10

        # 总数目和总金额
        total_count = 0
        total_price = 0

        # todo: 向df_order_info表中添加一条记录
        order = OrderInfo.objects.create(order_id=order_id,
                                         user=user,
                                         addr=addr,
                                         pay_method=pay_method,
                                         total_count=total_count,
                                         total_price=total_price,
                                         transit_price=transit_price)

        # todo: 用户的订单中有几个商品，需要向df_order_goods表中加入几条记录
        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id

        sku_ids = sku_ids.split(',')
        for sku_id in sku_ids:
            # 获取商品的信息
            try:
                sku = GoodsSKU.objects.get(id=sku_id)
            except:
                # 商品不存在
                return JsonResponse({'res':4, 'errmsg':'商品不存在'})

            # 从redis中获取用户所要购买的商品的数量
            count = conn.hget(cart_key, sku_id)

            # todo: 向df_order_goods表中添加一条记录
            OrderGoods.objects.create(order=order,
                                      sku=sku,
                                      count=count,
                                      price=sku.price)

            # todo: 更新商品的库存和销量
            sku.stock -= int(count)
            sku.sales += int(count)
            sku.save()

            # todo: 累加计算订单商品的总数量和总价格
            amount = sku.price*int(count)
            total_count += int(count)
            total_price += amount

        # todo: 更新订单信息表中的商品的总数量和总价格
        order.total_count = total_count
        order.total_price = total_price
        order.save()

        # todo: 清除用户购物车中对应的记录
        conn.hdel(cart_key, *sku_ids)

        # 返回应答
        return JsonResponse({'res':5, 'message':'创建成功'})

