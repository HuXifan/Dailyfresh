from goods.views import IndexView, DetailView, ListView
from django.conf.urls import include, url
from django.contrib import admin
from goods import views

urlpatterns = [
    url(r'^index$', IndexView.as_view(), name='index'),  # 首页
    url(r'^goods/(?P<goods_id>\d+)$', DetailView.as_view(), name='detail'),  # 详情
    url(r'^list/(?P<type_id>\d+)/(?P<page>\d+)$', ListView.as_view(), name='list'),  # /list/种类id/页码?sort=排序方式  列表页
]
