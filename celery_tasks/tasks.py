import time
from celery import Celery
from django.conf import settings
from django.shortcuts import render
from django.core.mail import send_mail
from django_redis import get_redis_connection
from django.template import loader, RequestContext

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")  # 设置环境变量,加载配置文件Settings
django.setup()  # django 环境初始化
# 以上四行加在任务处理者一端

from goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner

# 创建一个Celery的实例对象  ,broker 中间人任务队列
app = Celery('celery_tasks.tasks', broker='redis://10.10.21.29:6379/8')  # 使用redis指定8号数据库
# app = Celery('celery_tasks.tasks', broker='redis://0.0.0.0:6379/8')  # 使用redis指定8号数据库

# 定义任务函数,使用对象中的task方法进行装饰
@app.task
def send_register_active_email(to_email, username, token):
    # 发送激活邮件
    # 组织邮件信息
    subject = 'Django项目,天天生鲜'  # 邮件主题
    message = ''  # 邮件正文
    html_message = '<h1>%s,欢迎您成为天天生鲜注册会员</h1>请点击下方激活您的账户<br><a href="http:127.0.0.1:8000/user/active/%s">http:127.0.0.1:8000/user/active/%s</a>' % (
        username, token, token)
    sender = settings.EMAIL_FROM  # 发件人
    receiver = [to_email]  # 收件人,列表-->用户的注册邮箱
    send_mail(subject, message, sender, receiver, html_message=html_message)
    time.sleep(5)


'''
注意:发出者处理者task代码要一致,每次更新每次同步OK
'''


# 　app对象进行装饰
@app.task
def generate_static_index_html():
    '''产生首页静态页面'''
    # 获取商品的种类信息
    types = GoodsType.objects.all()

    # 获取首页轮播商品信息
    goods_banners = IndexGoodsBanner.objects.all().order_by('index')

    # 获取首页促销活动信息
    promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

    # 获取首页分类商品展示信息
    for type in types:  # GoodsType
        # 获取type种类首页分类商品的图片展示信息
        image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
        # 获取type种类首页分类商品的文字展示信息
        title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')

        # 动态给type增加属性，分别保存首页分类商品的图片展示信息和文字展示信息
        type.image_banners = image_banners
        type.title_banners = title_banners

    # 组织模板上下文
    context = {'types': types,
               'goods_banners': goods_banners,
               'promotion_banners': promotion_banners,
               }

    # 使用模板
    # return render(request, 'index.html', context)
    # 1 加载模板文件,返回模板对象
    temp = loader.get_template('static_index.html')

    # 2 定义模板上下文
    # context = RequestContext(request, context)  # 定义模板渲染的时候，不需要依赖与request

    # 2 模板渲染
    static_index_html = temp.render(context)  # 替换并返回
    # print(static_index_html)

    # 3 2是页面,3生成页面
    save_path = os.path.join(settings.BASE_DIR, 'static/index.html')
    print(save_path)
    with open(save_path, 'w') as f:
        f.write(static_index_html)  # 把渲染后的内容写到文件里面
