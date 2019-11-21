from goods.views import IndexView
from django.conf.urls import include, url
from django.contrib import admin
from goods import views
urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index')  # 首页
]
