
from django.conf.urls import include, url
from django.contrib import admin
from apps.user import views
urlpatterns = [
    url(r'^register', views.register, name='register')  # 注册 # 使用反向解析添加name属性

]
