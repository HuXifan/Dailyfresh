# Python-Django-天天生鲜项目

初学django框架时按照传智播客python教程所学习的项目,该项目包含了实际开发中的电商项目中大部分的功能开发和知识点实践。

功能:用户注册，用户登录，购物车，用户中心，首页，订单系统，地址信息管理，商品列表，商品详情，支付功能等等，是一个完整的电商项目流程

__注:此项目纯属个人学习项目__

## 技术栈
python + django + mysql + redis + celery + FastDFS(分布式图片服务器) + nginx


## 目标功能:
- [x] 功能模块
    - [x] 用户模块
        - [x] 注册
        - [x] 登录
        - [x] 激活(celery)
        - [x] 退出
        - [x] 个人中心
        - [x] 地址管理
    - [x] 商品模块
        - [x] 首页(celery)
        - [x] 商品详情
        - [x] 商品列表
        - [x] 搜索功能(haystack+whoose)
    - [x] 购物车模块(redis)
        - [x] 增加
        - [x] 删除
        - [x] 修改
        - [x] 查询
    - [x] 订单模块
        - [x] 确认订单页面
        - [x] 订单创建
        - [x] 请求支付(支付宝)
        - [x] 查询支付结果
        - [x] 评论

## 运行环境

[配置环境文件](./configurationFile/images/fehelper-github-com-yuanwenq-dailyfresh-blob-dev-dailyfresh-settings-py-1544797232546.png)

[虚拟环境安装和启动方式](configurationFile/virtualenvDescript.md)

[celery分布式任务队列](configurationFile/celeryDescript.md)

[redis环境安装](./configurationFile/redisDownload.md)

[FastDFS安装和配置](./configurationFile/fastDFSDownload.md)

[Nginx及fastdfs-nginx-module安装](./configurationFile/nginxAndFastDFS-nginx-moduleDownload.md)

[全文检索引擎-生成jieba分词引擎步骤](./configurationFile/Full-textSearchEngine.md)

[支付宝支付配置](https://github.com/fzlee/alipay/blob/master/README.zh-hans.md)

[软件安装-云盘](https://pan.baidu.com/s/1NkK7VbeNBrbTPUeTxcYD6A)
  
- 项目启动：  
    - **注意: 项目启动前请先查看项目[配置环境文件](./configurationFile/images/fehelper-github-com-yuanwenq-dailyfresh-blob-dev-dailyfresh-settings-py-1544797232546.png),配置你相应的设置,并安装好各个环境,mysql+redis+nginx+fastDFS+celery等**
        ```
        项目包安装
        pip install -r requirements.txt
        
        Django启动命令
        python manage.py runserver 
        ```    
- uwsgi web服务器启动：  
    - **注意: uwsgi开启需要修改[配置文件](./dailyfresh/settings.py)中的DEBUG和ALLOWED_HOSTS**
        ```    
        启动: uwsgi --ini 配置文件路径 / uwsgi --ini uwsgi.ini
        停止: uwsgi --stop uwsgi.pid路径 / uwsgi --stop uwsgi.pid
        ```
- celery分布式任务队列启动  
        ```
        celery -A celery_tasks.tasks worker -l info
        ```
- redis服务端启动  
        ```
        sudo redis-server /etc/redis.conf
        ```
- FastDFS服务启动
        ```    
        Trackerd服务
        sudo /usr/bin/fdfs_trackerd /etc/fdfs/tracker.conf start
    
        storge服务
        sudo /usr/bin/fdfs_storaged /etc/fdfs/storage.conf start
        ```
- nginx
    ```
    启动nginx
    sudo /usr/local/nginx/sbin/nginx
    重启nginx
    sudo /usr/local/nginx/sbin/nginx -s reload
    ```
- 建立索引文件--搜索引擎  
  新环境需要配置jieba分词,生成[whoose_cn_backend]()文件
    ```
    python manage.py rebuild_index
    ```
- mysql事务隔离级别设置
    ```
    sudo vim /etc/mysql/mysql.conf.d/mysql.cnf
    transaction-isolation = READ-COMMITTED (读已提交)
    ```
## 项目包介绍
```
amqp==2.3.2
asn1crypto==0.24.0
billiard==3.5.0.4
celery==4.2.1
certifi==2018.11.29
cffi==1.11.5
chardet==3.0.4
configparser==3.5.0
cryptography==2.4.1
Django==1.8.2
django-haystack==2.8.1
django-redis==4.10.0
django-redis-sessions==0.5.6
django-tinymce==2.6.0
fdfs-client-py==1.2.6
idna==2.7
itsdangerous==1.1.0   # 身份信息加密
jieba==0.39           # jieba分词-分解词汇方便搜索   
kombu==4.2.1
mutagen==1.41.1
Pillow==5.3.0
pycparser==2.19
pycryptodomex==3.7.2
PyMySQL==0.9.2
python-alipay-sdk==1.8.0
pytz==2018.7
redis==2.10.6
requests==2.20.1
rerequests==1.0.0b0
six==1.11.0
urllib3==1.24.1
uWSGI==2.0.17.1
vine==1.1.4
Whoosh==2.7.4
```

## 开发方法
### 用户认证模型
```
# django认证系统使用的用户模型
AUTH_USER_MODEL = "users.User"
```
- Django发送邮件
   - Django网站 ---> smtp服务器 ---> 目的邮箱
- celery:异步任务队列
    - 任务的发出者、中间人、任务的处理者可以在同一台电脑上启动，也可以不在同一台电脑上。处理者也需要任务的代码，任务处理者所在电脑必须有网,即能和外机通信.
    `pip install celery 
    `
     - 项目代码（任务发出者）—发出任务—>任务队列（中间人broker）redis<—监听任务队列—任务处理者worker
- 用户激活
    - 使用itsdangerous加密用户身份信息
    - ```python
        # 加密用户的身份信息，生成激活token
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm':user.id}
        token = serializer.dumps(info)
        token = token.decode()
        ```  
    - 解密用户身份信息
        ```python
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            # 根据秘钥解密
            info = serializer.loads(token)
            # 获取待激活用户的id
            user_id = info['confirm']
            # 根据id获取用户信息
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            # 跳转到登录页面
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            return HttpResponse('激活连接已过期！')
        ```  
- 用户登录
    - 配置redis作为Django缓存和session后端
    ```python
    # Django的缓存配置
    CACHES = {
        "default":{
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://172.16.179.142:6379/9",
            "OPTIONS":{
                "CLIENT_CLASS":"django_redis.client.DefaultClient",
        }
        }
    }
    # 配置sessiong存储
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"
    ```
    - 登录判断装饰器loging_required
    ```pytho        n
    from django.contrib.auth.decorators import login_required
    # 使用LoginRequireMixin：
    class LoginRequiredMixin(object):
        @classmethod
        def as_view(cls, **initkwargs):
            # 调用父类的as_view
            view = super(LoginRequiredMinxin, cls).as_view(**initkwargs)
            return login_required(view)
    ```
    ```python
    # 登陆后跳转 --> 获取登录后所需要跳转的地址
    # 默认跳转到首页
    next_url = request.GET.get('next', reverse('goods:index'))
    # 跳转到next_url
    response = redirect(next_url) # 重定向到新的地址
    ```
### 商品模块开发
- FastDFS分布式文件系统
    - 配置服务  `tracker_server = ip地址：22122`
    - 启动tracker,storage, nginx服务
        ```python
            sudo service fdfs trackerd start
            sudo service fsfs storaged start
            sudo /usr/local/nginx/sbin/nginx
        ```
    - 执行测试命令 `fdfs_upload_file /etc/fdfs/client.conf`
    
- **nginx特点**
    - 海量存储，存储容量扩展方便。  
    - 文件内容重复时只保留一份。
    - 结合nginx提高网站访问图片的效率`
    
### 商品首页
- redis保存用户的购物车记录
    - 采用的数据形式：每个用户的购物车记录用一条数据保存：
    hash：
    cart_用户id：{‘SKU_ID1’:数量，‘sku_id2’:数量}
- 页面静态化
    - 把原本动态的页面处理结果保存成html文件，让用户直接访问这个生成出来的静态的html页面
    `①使用celery生成静态页面
    ②配置nginx提供静态页面
    ③管理员修改首页所使用表中的数据时，重新生成index静态页面`  
   
- 页面数据的缓存
    - 把页面使用的数据放在缓存中,当再次使用这些数据时先从缓存中获取,如果获取不到,再去查询数据库
    - 作用: 减少数据库查询次数
    - 当管理员修改首页信息对应数据表数据时需要更新缓存

### 商品搜索
 - 搜索引擎:
    1）可以对表中的某些字段进行关键词分析，简历关键词对应的索引数据。
    索引：字典目录
    全文检索框架：可以帮助用户使用搜索引擎。
    用户----》全文检索框架haystack-----》搜索引擎whoosh
 - 搜索引擎配置    
    添加、修改、删除数据时，自动生成索引
    `HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'`
    `# 指定搜索结果每一页搜索条数
    HAYSTACK_SEARCH_RESULTS_PER_PAGE = 2`
    ```
    HAYSTACK_CONNECTIONS = {
    'default': {
        # 使用whoosh引擎 /home/huxf/.pyenv/versions/dj182/lib/python3.5/site-packages/haystack/backends
        # 'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',  # 原始配置
        'ENGINE': 'haystack.backends.whoosh_cn_backend.WhooshEngine',  # 使用自定义的jieba分词的引擎
        # 设置索引文件生成路径
        'PATH': os.path.join(BASE_DIR, 'whoosh_index'),
        }
    }
    ```  
### 购物车模块开发
- 添加到购物车
    - 购物车后台视图函数:设计数据增删改查,(POST方法)
        - 先判断用户是否登录
        ```
        user = request.user
        # 判断用户有没有登录
        if not user.is_authenticated():
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})
        ```
        - 接收数据,校验数据,加购,校验库存
        ```
        # 接收数据
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')
        # 数据校验
        if not all([sku_id, count]):
            return JsonResponse({'res': 1, 'errmsg': '数据不完整'})
        # 校验添加的商品数量
        try:
            count = int(count)
        except Exception as e:
            # 数目出错
            return JsonResponse({'res': 2, 'errmsg': '商品数目出错'})
        # 校验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            # 商品不存在
            return JsonResponse({'res': 3, 'errmsg': '商品不存在'})
        # 业务处理:添加购物车记录
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        # 尝试获取sku_id的值 hget cart_key  属性
        cart_count = conn.hget(cart_key, sku_id)  # 如果sku_id不存在 返回none
        if cart_count:
            # 有值 > 累加购物车数目
            count += int(cart_count)
        # 校验商品的库存
        if count > sku.stock:
            return JsonResponse({'res': 4, 'errmsg': '库存不足'})
        # 设置hash中sku_id对应的值
        conn.hset(cart_key, sku_id, count)  # hset 存在就是更新.不存在就是新增
        # 计算用户购物车商品条目数
        total_count = conn.hlen(cart_key)
        # 返回应答
        return JsonResponse({'res': 5, 'total_count': total_count, 'message': '添加购物车成功'})

        ```
    - 详情页面加购显示
        - 设计计算商品总价函数
        ```
        function update_goods_amount() {
            // 获取商品的单价和数量
            price = $('.show_pirze').children('em').text()
            count = $('.num_show').val()
            // 计算商品的总价
            price = parseFloat(price) // 转化小数
            count = parseInt(count)
            amount = price * count
            // 设置商品的总价，toFixed(2) 保留两位小数
            $('.total').children('em').text(amount.toFixed(2) + '元')
        }
        ```
        - 增加,减少,手动,输入加购数量
    - 注意点 <strong><em>csrf</em>
        - django默认打开csrf中间件
        - 表单post提交数据时加上{% csrf_token %} 标签
        `// <input type='hidden' name='csrfmiddlewaretoken' value='PJtbb4j2QJHMWht3KkJIrLEOAnsyfIW1' />`
        </br>` csrf = $('input[name="csrfmiddlewaretoken"]').val()`
        - 防御原理:
            - 渲染模板文件时在页面生成一个名字叫做 csrfmiddlewaretoken 的隐藏域.
            - 服务器交给浏览器保存一个名字为 csrftoken的cookie信息
            - 提交表单时,两个值都会发给服务器,服务器进行对比,如果一样,csrf验证通过,否则失败,报403错误.
                    
- 购物车页面
    - 数据获取
        - 合计数目=所有商品数目总和
        - 合计金额=各商品小计总和
        - 搜索框单独设置
            - 搜索购物车内商品
    - 页面数据更新
    

- 购物车记录更新/删除

### 订单模块开发
- 提交订单页面
    - 模板变量:sku(动态追加商品小计,购买商品的数量),总价,总数量,运费,总支付款,收货地址
- 订单生成
    - 前端传递的参数:地址id,支付方式pay_method,用户要购买的商品id:sku_ids
    - 向后台数据库添加记录
      ```
      order = OrderInfo.objects.create(order_id=order_id,
                                         user=user, addr=addr,
                                         pay_method=pay_method,
                                         total_count=total_count,
                                         total_price=total_price,
                                         transit_price=transit_price)
      ```
      ```
      for sku_id in sku_ids:
        # 获取商品信息
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except:
            return JsonResponse({'res': 4, 'errmsg': '商品不存在'})

        # 从redis中获取用户索要购买的商品数量
        count = conn.hget(cart_key, sku_id)

        # 向df_order＿info添加几条记录,遍历,有几条就加几条记录
        OrderGoods.objects.create(order=order,
                                  sku=sku,
                                  count=count,
                                  price=sku.price)
        # todo 更新商品的库存和销量
        sku.stock -= int(count)
        sku.sales += int(count)
        sku.save()

        # 累加计算订单商品的总数目 总价格
        amount = sku.price * int(count)
        total_count += int(count)
        total_price += amount
      ``` 
      ```
        # 出了循环外 更新订单信息表中的商品总数量和总价格
        order.total_count = total_count
        order.total_price = total_price
        order.save()
        # 清除购物车里用户购买过的商品记录
        conn.hdel(cart_key, *sku_ids)
      ```


## 注意点
redis版本需要2.10.6 否则会报错,因为使用django的版本(1.8.2)过低问题  
如果使用乐观锁,需要修改mysql事务的隔离级别设置

## 总结

## 项目展示

## 项目布局
```
|-- README.md
|-- __init__.py
|-- apps                        
|   |-- __init__.py
|   |-- cart                            
|   |   |-- __init__.py
|   |   |-- __pycache__
|   |   |-- admin.py
|   |   |-- migrations          
|   |   |   |-- __init__.py
|   |   |   `-- __pycache__
|   |   |-- models.py
|   |   |-- tests.py
|   |   |-- urls.py
|   |   `-- views.py
|   |-- goods                   
|   |   |-- __init__.py
|   |   |-- __pycache__
|   |   |-- admin.py
|   |   |-- migrations
|   |   |   |-- 0001_initial.py
|   |   |   |-- __init__.py
|   |   |   `-- __pycache__
|   |   |       |-- 0001_initial.cpython-36.pyc
|   |   |-- models.py
|   |   |-- search_indexes.py
|   |   |-- tests.py
|   |   |-- urls.py
|   |   `-- views.py
|   |-- order
|   |   |-- __init__.py
|   |   |-- __pycache__
|   |   |-- admin.py
|   |   |-- alipay_public_key.pem
|   |   |-- app_private_key.pem
|   |   |-- migrations
|   |   |   |-- 0001_initial.py
|   |   |   |-- 0002_auto_20181126_1609.py
|   |   |   |-- __init__.py
|   |   |   `-- __pycache__
|   |   |-- models.py
|   |   |-- tests.py
|   |   |-- urls.py
|   |   `-- views.py
|   `-- user
|       |-- __init__.py
|       |-- __pycache__
|       |-- admin.py
|       |-- migrations
|       |   |-- 0001_initial.py
|       |   |-- __init__.py
|       |   `-- __pycache__
|       |-- models.py
|       |-- tests.py
|       |-- urls.py
|       `-- views.py
|-- celery_tasks
|   |-- __init__.py
|   |-- __pycache__
|   `-- tasks.py
|-- configurationFile
|   |-- Full-textSearchEngine.md
|   |-- celeryDescript.md
|   |-- conf
|   |   |-- client.conf
|   |   |-- mod_fastdfs.conf
|   |   |-- nginx.conf
|   |   |-- redis.conf
|   |   |-- search.png
|   |   |-- storage.conf
|   |   |-- tracker.conf
|   |   `-- whoosh_cn_backend.py
|   |-- fastDFSDownload.md
|   |-- images
|   |-- nginxAndFastDFS-nginx-moduleDownload.md
|   |-- redisDownload.md
|   `-- virtualenvDescript.md
|-- dailyfresh
|   |-- __init__.py
|   |-- __pycache__
|   |-- settings.py
|   |-- urls.py
|   `-- wsgi.py
|-- db
|   |-- __init__.py
|   |-- __pycache__
|   `-- base_model.py
|-- manage.py
|-- mind.md
|-- nginxConfig
|-- requirements.txt
|-- static
|   |-- cart.html
|   |-- css
|   |-- detail.html
|   |-- images
|   |-- index.html
|   |-- js
|   |   |-- jquery-1.12.4.min.js
|   |   |-- jquery-ui.min.js
|   |   |-- jquery.cookie.js
|   |   |-- register.js
|   |   `-- slide.js
|   |-- list.html
|   |-- login.html
|   |-- place_order.html
|   |-- register.html
|   |-- user_center_info.html
|   |-- user_center_order.html
|   `-- user_center_site.html
|-- templates
|   |-- base.html
|   |-- base_detail_list.html
|   |-- base_no_cart.html
|   |-- base_user_center.html
|   |-- cart.html
|   |-- detail.html
|   |-- index.html
|   |-- list.html
|   |-- login.html
|   |-- order_comment.html
|   |-- place_order.html
|   |-- register.html
|   |-- search
|   |   |-- indexes
|   |   |   `-- goods
|   |   |       `-- goodssku_text.txt
|   |   |-- search.html
|   |   `-- search1.html
|   |-- static_base.html
|   |-- static_index.html
|   |-- user_center_info.html
|   |-- user_center_order.html
|   `-- user_center_site.html
|-- utils
|   |-- __init__.py
|   |-- __pycache__
|   |-- fdfs
|   |   |-- __init__.py
|   |   |-- __pycache__
|   |   |-- client.conf
|   |   `-- storage.py
|   `-- mixin.py
|-- uwsgi
|-- uwsgi.log
|-- uwsgi.pid
|-- uwsgi2
|-- uwsgi2.log
|-- uwsgi2.pid
`-- whoosh_index                    
    |-- MAIN_WRITELOCK
    |-- MAIN_o1a38vfacpcxkfgw.seg
    `-- _MAIN_11.toc
```

## mysql数据库展示
```
+--------------------------+
| Tables_in_dailyfresh     |
+--------------------------+
| auth_group               |
| auth_group_permissions   |
| auth_permission          |
| df_address               |
| df_goods                 |
| df_goods_image           |
| df_goods_sku             |
| df_goods_type            |
| df_index_banner          |
| df_index_promotion       |
| df_index_type_goods      |
| df_order_goods           |
| df_order_info            |
| df_user                  |
| df_user_groups           |
| df_user_user_permissions |
| django_admin_log         |
| django_content_type      |
| django_migrations        |
| django_session           |
+--------------------------+

```