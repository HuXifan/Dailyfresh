from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from apps.user import views
from user.views import RegisterView, ActiveView, LoginView, UserInfoView, UserOrderView, AddressView
urlpatterns = [
    # url(r'^register$', views.register, name='register'),  # 注册 # 使用反向解析添加name属性
    # url(r'^register_handler$', views.register_handle, name='register_handler'),  # 注册处理
    url(r'^register$', RegisterView.as_view(), name='register'),  # 注册
    url(r'^active/(?P<token>.*)$', ActiveView.as_view(), name='active'),  # 用户激活的url配置
    url(r'^login$', LoginView.as_view(), name='login'),  # 登录

    url(r'^$', login_required(UserInfoView.as_view()), name='user'),  # 用户中心-信息页
    url(r'^order$', login_required(UserOrderView.as_view()), name='order'),  # 用户中心订单页
    url(r'^address$', login_required(AddressView.as_view()), name='address'),  # 用户中心-地址页


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
