from django.conf.urls import include, url
from django.contrib import admin
from apps.user import views
app_name = 'user'
urlpatterns = [
    url(r'^register$', views.register, name='register'),  # 注册 # 使用反向解析添加name属性
    url(r'^register_handler$', views.register_handle, name='register_handler'),  # 注册处理

]
