from django.conf.urls import include, url
from django.contrib import admin
from apps.user import views
from user.views import RegisterView

urlpatterns = [
    # url(r'^register$', views.register, name='register'),  # 注册 # 使用反向解析添加name属性
    # url(r'^register_handler$', views.register_handle, name='register_handler'),  # 注册处理
    url(r'^register$', RegisterView.as_view(), name='register')  # 注册

]


'''
def view(request, *args, **kwargs):
    self = cls(**initkwargs)
    if hasattr(self, 'get') and not hasattr(self, 'head'):
        self.head = self.get
    self.request = request
    self.args = args
    self.kwargs = kwargs
    return self.dispatch(request, *args, **kwargs)  # 分发
'''