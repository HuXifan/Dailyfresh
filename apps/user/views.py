import re
from django.shortcuts import render, redirect
from django.http import HttpResponse
# from django.urls import reverse
from django.core.urlresolvers import reverse
from django.core.mail import send_mail  #
from django.views.generic import View
from user.models import User
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer  # 帮助实现加密
from itsdangerous import SignatureExpired  # 异常


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

        # 发送激活邮件 包含激活链接:激活链接中需要包含用户身份信息:用户名或者ID /user/active
        # http://127.0.0.1:8000/user/active/jiamixinxi  需要包含身份信息进行加密
        # 返回应答,跳转首页,使用反向解析函数

        # 1 加密用户身份信息,生成激活token,使用Django自带的在Settings中的秘钥,设置过期时间一小时
        serializer = Serializer(settings.SECRET_KEY, 3600)
        # 2 加密
        info = {'confirm': user.id}
        token = serializer.dumps(info)  # 加密后的token

        # 发邮件
        subject = 'Django项目,天天生鲜'
        message = 'information'
        sender = settings.EMAIL_FROM  # 发件人
        receiver = [email]
        send_mail(subject, message, sender, recipient_list=receiver)

        # 返回应答,跳转首页,使用反向解析函数
        return redirect(reverse('goods:index'))

    def put(self, request):
        pass


'''类视图原理'''


class ActiveView(View):
    # 用户激活
    def get(self, request, token):
        # 进行解密 获取要激活的用户信息
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)  # 接token,loads解密
            # 获取激活用户的id
            user_id = info['confirm']
            # 根据id获取用户信息
            user = User.objects.get(id=user_id)
            # 更改激活标记
            user.is_active = 1
            user.save()

            # 返回一个应该,跳转登录页面:使用反向解析
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            # 异常 激活链接已过期
            return HttpResponse("激活链接已经过期")


# /user/login
class LoginView(View):
    # 登录
    def get(self, request):
        # 显示登录页面
        return render(request, 'login.html')
