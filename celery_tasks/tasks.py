import time
from celery import Celery
from django.conf import settings
from django.core.mail import send_mail

import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
django.setup()  # 以上四行加在任务处理者一端

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


