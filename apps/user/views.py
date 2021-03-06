import re
import redis
from redis import StrictRedis
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.core.mail import send_mail  # 发送邮件函数
from django.views.generic import View
from user.models import User, Address
from goods.models import GoodsSKU
from order.models import OrderInfo, OrderGoods
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer  # 帮助实现加密
from itsdangerous import SignatureExpired  # 异常
from celery_tasks.tasks import send_register_active_email  # 导入发送邮件任务函数
from django.contrib.auth import authenticate, login, logout  # 用户认证　登录　登出　Django
from utils.mixin import LoginRequiredMixin
from django_redis import get_redis_connection


# Create your views here.
# GET/POST
def register(request):
    # 显示注册页面
    if request.method == 'GET':
        # 显示注册页面
        return render(request, 'register.html')
    else:
        # 进行注册处理
        # 浏览器发过来数据就进行接收
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        cpwd = request.POST.get('cpwd')  # 确认密码
        allow = request.POST.get('allow')

        # 进行数据校验  # 可迭代的东西
        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)  # get会查到一条进一条查不到会
        except User.DoesNotExist:
            # 抛异常用户名不存在,未注册
            user = None
        if user:
            # 用户名已经存在
            return render(request, 'register.html', {'errmsg': '该用户名已被注册'})

        # 验证数据完整性
        if not all([username, password, email]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '注册数据不完整!'})
        # 校验邮箱有效合法
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            # 不是有效合法的邮箱
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确!'})
        # 校验两次密码一致性
        if password != cpwd:
            return render(request, 'register.html', {'errmsg': '两次输入的密码不一致!'})
        # 是否同意协议
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议!'})
        # 进行业务处理:流程:进行用户注册
        # user = User()  # 创建用户对象,保存用户数据
        # user.username = username
        # user.password = password
        # user.email = email
        # user.save()
        user = User.objects.create_user(username, email, password)  # username,email,password顺序不能错
        user.is_active = 0  # 设置没有激活
        user.save()  # 保存

        # 发送激活邮件 包含激活链接:激活链接中需要包含用户身份信息:用户名或者ID /user/active
        # http://127.0.0.1:8000/user/active/id   需要被身份信息进行加密
        # 返回应答,跳转首页,使用反向解析函数
        return redirect(reverse('goods:index'))


def register_handle(request):
    # 进行注册处理
    # 浏览器发过来数据就进行接收
    username = request.POST.get('user_name')
    password = request.POST.get('pwd')
    email = request.POST.get('email')
    cpwd = request.POST.get('cpwd')
    allow = request.POST.get('allow')

    # 进行数据校验  # 可迭代的东西
    # 校验用户名是否重复
    try:
        user = User.objects.get(username=username)  # get会查到一条进一条查不到会
    except User.DoesNotExist:
        # 抛异常用户名不存在
        user = None
    if user:
        # 用户名已经存在
        return render(request, 'register.html', {'errmsg': '该用户名已被注册'})

    if not all([username, password, email]):
        # 数据不完整
        return render(request, 'register.html', {'errmsg': '注册数据不完整!'})
    # 校验邮箱
    if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
        # 不是有效合法的邮箱
        return render(request, 'register.html', {'errmsg': '邮箱格式不正确!'})
    # 校验两次密码一致性
    if password != cpwd:
        return render(request, 'register.html', {'errmsg': '两次输入的密码不一致!'})
    # 是否同意协议
    if allow != 'on':
        return render(request, 'register.html', {'errmsg': '请同意协议!'})
    # 进行业务处理:流程:进行用户注册
    # user = User()  # 创建用户对象,保存用户数据
    # user.username = username
    # user.password = password
    # user.email = email
    # user.save()
    user = User.objects.create_user(username, email, password)  # username,email,password顺序不能错
    user.is_active = 0  # 设置没有激活
    user.save()  # 保存

    # 返回应答,跳转首页,使用反向解析函数
    return redirect(reverse('goods:index'))


class RegisterView(View):
    '''类视图,限定请求方式对应的处理:不同请求方式get/post对应不同的函数'''

    def get(self, request):
        # x 显示注册页面
        return render(request, 'register.html')

    def post(self, request):

        # 进行注册处理
        # 浏览器发过来数据就进行接收
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        cpwd = request.POST.get('cpwd')  # 确认密码
        allow = request.POST.get('allow')

        # 进行数据校验  # 可迭代的东西
        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)  # get会查到一条,一条查不到会
        except User.DoesNotExist:
            # 抛异常用户名不存在
            user = None
        if user:
            # 用户名已经存在
            return render(request, 'register.html', {'errmsg': '该用户名已被注册'})

        if not all([username, password, email]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '注册数据不完整!'})
        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            # 不是有效合法的邮箱
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确!'})
        # 校验两次密码一致性
        if password != cpwd:
            return render(request, 'register.html', {'errmsg': '两次输入的密码不一致!'})
        # 是否同意协议
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议!'})
        # 进行业务处理:流程:进行用户注册
        # user = User()  # 创建用户对象,保存用户数据
        # user.username = username
        # user.password = password
        # user.email = email
        # user.save()
        user = User.objects.create_user(username, email, password)  # username,email,password顺序不能错
        user.is_active = 0  # 设置没有激活
        user.save()  # 保存

        # 发送激活邮件 包含激活链接:激活链接中需要包含用户身份信息:用户名或者ID /user/active
        # http://127.0.0.1:8000/user/active/jiamixinxi  需要包含身份信息进行加密
        # 返回应答,跳转首页,使用反向解析函数

        # 1 加密用户身份信息,生成激活token,使用Django自带的在Settings中的秘钥,设置过期时间一小时
        serializer = Serializer(settings.SECRET_KEY, 3600)
        # 2 加密
        info = {'confirm': user.id}
        token = serializer.dumps(info)  # 加密后的token,返回的是bytes字节流数据
        token = token.decode()

        # 发邮件
        # subject = 'Django项目,天天生鲜'  # 邮件主题
        # message = ''  # 邮件正文
        # html_message = '<h1>%s,欢迎您成为天天生鲜注册会员</h1>请点击下方激活您的账户<br><a href="http:127.0.0.1:8000/user/active/%s">http:127.0.0.1:8000/user/active/%s</a>' % (
        #     username, token, token)
        # sender = settings.EMAIL_FROM  # 发件人
        # receiver = [email]  # 收件人,列表-->用户的注册邮箱
        # send_mail(subject, message, sender, receiver, html_message=html_message)
        # 专门的参数html_message

        # 发邮件替换为异步使用celery, '任务函数名字'.delay()发出任务,加入任务队列
        send_register_active_email.delay(email, username, token)  # 收件人，用户名,token

        # 返回应答,跳转首页,使用反向解析函数
        return redirect(reverse('goods:index'))

    def put(self, request):
        pass


'''类视图原理'''


class ActiveView(View):

    # 用户激活
    def get(self, request, token):
        # 进行解密 获取要激活的用户信息
        serializer = Serializer(settings.SECRET_KEY, 3600)  # 和加密时一样
        try:
            info = serializer.loads(token)  # 接token,loads解密
            user_id = info['confirm']  # 获取激活用户的id
            user = User.objects.get(id=user_id)  # 根据id获取用户信息
            # 更改激活标记
            user.is_active = 1
            user.save()
            # 返回一个应答,跳转登录页面:使用反向解析
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            # 异常 激活链接已过期
            return HttpResponse("激活链接已经过期")


# /user/login
class LoginView(View):
    # 登录
    def get(self, request):
        # 显示登录页面
        # 判断是否记住了用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')  # 在COOKIE里就获取
            checked = 'checked'
        else:
            username = ''
            checked = ''
        # 使用模板
        return render(request, 'login.html', {'username': username, 'checked': checked})

    def post(self, request):
        # 登录校验:  -> 接收数据,校验数据,业务处理:登录校验,登陆处理
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        # 校验数据 合法性
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '数据不完整'})
        # 登录校验
        # User.objects.get(username=username, password=password)

        # django自带的user认证
        user = authenticate(username=username, password=password)
        if user is not None:
            # the password verified for the user 用户名密码正确
            if user.is_active:
                # 用户已经激活
                print("User is valid, active and authenticated")
                # 　记录用户登录状态
                login(request, user)
                '''下面是django.contrib.auth.views.login所做的事情：
                如果通过 GET调用，它显示一个POST给相同URL的登录表单。后面有更多这方面的信息。
                如果通过POST调用并带有用户提交的凭证，它会尝试登入该用户。如果登入成功，该视图重定向到next中指定的URL。如果next没有提供，它重定向到settings.LOGIN_REDIRECT_URL（默认为/accounts/profile/）。如果登入不成功，则重新显示登录表单。'''
                # 获取登录后所要跳转的地址,如果next返回值,get就会返回,如果获取不到(None),返回默认的值:默认首页
                next_url = request.GET.get('next', reverse('goods:index'))
                response = redirect(next_url)
                # 跳转到首页
                # response = redirect(reverse('goods:index'))  # HttpResponseRedirect

                # 判断是否需要记住用户名
                remember = request.POST.get('remember')
                if remember == 'on':
                    # 需要记住用户名,设置cookie,过期时间一周
                    response.set_cookie('username', username, max_age=7 * 24 * 3600)
                else:
                    # 不需要记住用户名
                    response.delete_cookie('username')

                # 返回相应
                return response

            else:
                # 用户未激活
                print("The password is valid, but the account has been disabled!")
                return render(request, 'login.html', {'errmsg': '账户未激活'})
        else:
            # the authentication system was unable to verify the username and password
            # 用户名或密码错误
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})


# 登出  /user/logout
class LogoutView(View):
    def get(self, request):
        # 退出登录
        logout(request)  # Redirect to a success page.
        # 当你调用logout()时，当前请求的会话数据将被完全清除。所有存在的数据都将清除。(清除session)
        # 这是为了防止另外一个人使用相同的Web浏览器登入并访问前一个用户的会话数据。
        # 如果你想在用户登出之后>可以立即访问放入会话中的数据，请在调用django.contrib.auth.logout()之后放入。
        return redirect(reverse('goods:index'))


# 以下三个视图类继承自LoginRequireMixin,封装了需要登录才能访问的功能先继承LOGINRequiredMixin ,后继承view
# /user
class UserInfoView(LoginRequiredMixin, View):
    # 显示用户中心页
    def get(self, request):
        # 显示
        # page='user'
        # if request.user.is_authenticated():
        # 除了你给模板文件传递的模板变量之外,Django框架会把request.user也传递给模板文件
        # 如果用户没有登录-> AnonmouseUser的一个实例
        # 如果用户已经登录-> User的一个实例,两个类都用有方法,在模板中可以直接使用User的对象和方法

        # 获取用户的个人信息
        user = request.user
        address = Address.objects.get_default_address(user)

        # 获取用户的最近浏览记录
        # sr = StrictRedis(host='127.0.0.1', port='6379', db=9)

        con = get_redis_connection('default')
        history_key = 'history_%d' % user.id
        # 获取用户前五条浏览记录商品的id
        sku_ids = con.lrange(history_key, 0, 4)  # 返回列表

        # 根据id查询用户浏览的商品的具体信息
        # goods_li = GoodsSKU.objects.filter(id_in=sku_ids)  # 返回列表查询集
        # goods_res = []
        # 两层循环，按照浏览顺序保存
        # for a_id in sku_ids:
        #     # a_id就会说用户浏览的id
        #     for goods in goods_li:
        #         if a_id == goods.id:
        #             goods_res.append(goods)

        goods_li = []
        # 遍历获取用户浏览的商品信息
        for id in sku_ids:
            goods = GoodsSKU.objects.get(id=id)
            goods_li.append(goods)

        # 组织上下文
        context = {'page': 'user', 'address': address, 'goods_li': goods_li}

        # 除了你给模板文件传递的模板变量外,Django还会吧request.user也传递给模板文件
        return render(request, 'user_center_info.html', context)


# /user/order
class UserOrderView(LoginRequiredMixin, View):
    # 显示用户中心页
    def get(self, request, page):
        # 显示用户的订单信息
        user = request.user

        # 查询用户的订单信息
        orders = OrderInfo.objects.filter(user=user).order_by('-create_time')

        # 遍历获取订单商品信息
        for order in orders:
            # 根据orderid查询商品信息
            order_skus = OrderGoods.objects.filter(order_id=order.order_id)
            # 遍历order_skus计算商品小计
            for order_sku in order_skus:
                # 计算小计
                amount = order_sku.count * order_sku.price
                # 动态给sku增加属性,保存订单商品小计
                order_sku.amount = amount

            # 动态给order增加属性,保存订单商品信息,订单状态
            order.status_name = OrderInfo.ORDER_STATUS[order.order_status]
            order.order_skus = order_skus

        # 分页
        paginator = Paginator(orders, 2)
        # 获取第page页的内容
        try:
            page = int(page)
        except Exception as e:
            page = 1  # 出错就显示第一页

        if page > paginator.num_pages:
            page = 1

        # 获取第page页的Page实例对象
        order_page = paginator.page(page)
        # 总页数小于5页,全部显示页数
        # 当前页是前三页,显示1-5页
        # 当前页的后三页，显示后5页
        # 其他情况，显示当前页的前两页当前页，当前页的后两页
        # 总页数大于5页,显示前两页和后面两页
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(page - 2, page + 3)

        # 组织上下文,使用模板
        context = {'order_page': order_page, 'pages': pages, 'page': 'order'}
        return render(request, 'user_center_order.html', context)


# /user/address
class AddressView(LoginRequiredMixin, View):
    # 显示用户中心页
    def get(self, request):
        # 显示
        # page='address'

        user = request.user  # 获取用户登录的User对象
        # 获取用户默认收地址
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     # 　不存在默认收货地址，赋值None
        #     address = None
        address = Address.objects.get_default_address(user)  # 以上方法的封装
        # 使用模板,传过去address
        return render(request, 'user_center_site.html', {'page': 'address', 'address': address})

    def post(self, request):
        # 添加地址:
        # 接受数据
        receiver = request.POST.get('receiver')  # 接受收件人信息
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')  # 手机
        # 数据校验:判断数据完整性
        if not all([receiver, addr, phone]):
            return render(request, 'user_center_site.html', {'errmsg': '数据不完整'})
        # 校验手机号
        if not re.match(r'^1[3|5|8|7|9][0-9]{9}$', phone):
            return render(request, 'user_center_site.html', {'errmsg': '手机格式不正确'})

        # 业务处理:地址添加
        # 如果已存在默认收货地址,添加的地址不作为默认收货地址,否则设置为默认地址
        # 先判断是否有默认收货地址,先导入模型类

        user = request.user  # 获取用户登录的User对象
        # try:
        #     address = Address.objects.get(user=user, is_default=True)  # models.Manager 对象
        # except Address.DoesNotExist:
        #     # 　不存在默认收货地址，赋值None
        #     address = None
        address = Address.objects.get_default_address(user)

        if address:
            # 不是None，已经有默认收货地址,定义一个变量is_default
            is_default = False
        else:
            is_default = True

        # 添加地址
        Address.objects.create(user=user,
                               receiver=receiver,
                               addr=addr,
                               zip_code=zip_code,
                               phone=phone,
                               is_default=is_default)

        # 返回应答,刷新地址页面
        return redirect(reverse('user:address'))  # get方式
