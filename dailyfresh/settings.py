"""
Django settings for dailyfresh project.

Generated by 'django-admin startproject' using Django 1.8.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))  # 加在第0个位置
# BASE_DIR = '/home/huxf/Dj18/dailyfresh'  # 项目的绝对路径
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# django内部的秘钥
SECRET_KEY = '5u4*w&yyy!q-!zcnij8ss=fot0uz&6x)evb5y+0gth6skmd#3b'  # 配置项内部的秘钥

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'apps.goods',
    # 'apps.cart',
    # 'apps.order',
    # 'apps.user',
    'tinymce',  # 富文本编辑器
    'user',  # 用户模块
    'goods',  # 商品模块
    'cart',  # 购物车模块
    'order',  # 订单模块

)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'dailyfresh.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'dailyfresh.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dailyfresh',
        'HOST': '10.10.21.29',  # 可远程
        'PORT': 3306,
        'USER': 'huxf',
        'PASSWORD': 'Root1'
    }
}

# 指定 Django认证系统使用的模型类
AUTH_USER_MODEL = 'user.User'  # 如果不指定,django会使用默认的模型类
# 指定后,不再生成auth_user的表,而是生成我们对应的user的表

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]  # 静态文件,目录

TINYMCE_DEFAULT_CONFIG = {
    # 富文本编辑器配置
    'theme': 'advanced',
    'height': '600',
    'width': '400',
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'  # 发邮件的SMTP服务器地址
EMAIL_PORT = 25
EMAIL_USE_TLS = True  # 邮箱连接失败增加项
# 发送邮件的邮箱
EMAIL_HOST_USER = 'huxifan666@163.com'
# 在邮箱中设置的客户端授权密码
EMAIL_HOST_PASSWORD = 'huxifan666'
# 收件人看到的发件人
EMAIL_FROM = 'python_Django<huxifan666@163.com>'
'''
服务器地址:
POP3服务器: pop.163.com
SMTP服务器: smtp.163.com

'''