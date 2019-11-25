from goods.views import IndexView, DetailView
from django.conf.urls import include, url
from django.contrib import admin
from goods import views
urlpatterns = [
    url(r'^index$', IndexView.as_view(), name='index') , # 首页
    url(r'^goods/(?P<goods_id>\d+)$', DetailView.as_view(), name='detail')  # 详情
]
