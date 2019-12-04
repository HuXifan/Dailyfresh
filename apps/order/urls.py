from django.conf.urls import include, url
from django.contrib import admin
from order.views import OrderPlaceView, OrderCommitView

urlpatterns = [
    url(r'^commit$', OrderCommitView.as_view(), name='commit'),  # 订单创建
    url(r'^place$', OrderPlaceView.as_view(), name='place'),  # 提交订单页面显示

]
