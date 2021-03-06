# Python-Django-天天生鲜项目

初学django框架时按照传智播客python教程所学习的项目,该项目包含了实际开发中的电商项目中大部分的功能开发和知识点实践。

功能:用户注册，用户登录，购物车，用户中心，首页，订单系统，地址信息管理，商品列表，商品详情，支付功能等等，是一个完整的电商项目流程

__注:此项目纯属个人学习项目__

## 技术栈
python + django + mysql + redis + celery + FastDFS(分布式图片服务器) + nginx

## 项目架构
- 前端
    - 用户相关
    - 商品相关
    - 购物车相关
    - 订单相关
    - 后台管理
- 后端
    - 用户模块
    - 商品模块
    - 购物车模块
    - 订单模块
    - 后台管理模块

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
        'uwsgi --ini uwsgi.ini'
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
## 项目所用包
```
amqp==2.5.1
billiard==3.5.0.2
celery==4.1.0
certifi==2019.9.11
cffi==1.13.2
chardet==3.0.4
cryptography==2.8
Django==1.8.2
django-haystack==2.8.1
django-redis==4.4.4
django-tinymce==2.6.0
fdfs-client-py==1.2.6
idna==2.8
importlib-metadata==0.23
itsdangerous==1.1.0
jieba==0.39
kombu==4.1.0
more-itertools==7.2.0
mutagen==1.42.0
Pillow==6.2.1
pycparser==2.19
pycryptodomex==3.9.4
PyMySQL==0.9.3
pyOpenSSL==19.1.0
python-alipay-sdk==2.0.0
pytz==2019.3
redis==2.10.6
requests==2.22.0
six==1.13.0
sqlparse==0.3.0
style==1.1.0
urllib3==1.25.7
uWSGI==2.0.18
vine==1.3.0
web.py==0.40.dev1
Whoosh==2.7.4
zipp==0.6.0
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
[]()
    - 任务的发出者、中间人、任务的处理者可以在同一台电脑上启动，也可以不在同一台电脑上。处理者也需要任务的代码，任务处理者所在电脑必须有网,即能和外机通信.
    `pip install celery     `
    - 项目代码（任务发出者）—发出任务—>任务队列（中间人broker）redis<—监听任务队列—任务处理者worker
- 用户激活
    - 使用itsdangerous加密用户身份信息
    - ```
        # 加密用户的身份信息，生成激活token
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm':user.id}
        token = serializer.dumps(info)
        token = token.decode()
      ```  
    - 解密用户身份信息
        ```
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
    ```
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
        ```
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
    - Django中使用事务
    原子性是由数据库的事务操作来界定的。atomic允许我们在执行代码块时，在数据库层面提供原子性保证。
    如果代码块成功完成，相应的变化会被提交到数据库进行commit；如果有异常，则更改将回滚。
        ```
        from django.db import transaction    
        @transaction.atomic
        def viewfunc(request):        
            do_stuff()
        ```
    - 悲观锁
        - 冲突比较少的时候使用,乐观锁使用代价比较大的时候使用(数据库操作时间长)
        - 特点:悲观锁获取数据时对数据行了锁定，其他事务要想获取锁，必须等原事务结束。
        ```
        # select * from df_goods_sku where id=sku_id for update # 悲观锁
        sku = GoodsSKU.objects.select_for_update().get(id=sku_id)
        ```
    - 乐观锁(冲突比较少的时候使用)
        - 改变事务级别(Django1.8.2)
        - 特点:查询时不锁数据，提交更改时进行判断.
        ```
        # update df_goods_sku set stock=new_stock, sales=new_sales where id=sku_id and stock = origin_stock
        # 返回受影响的行数
        res = GoodsSKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock,
                                                                            sales=new_sales)
        # 返回0 更新失败,返回1 更新成功
        if res == 0:
            if i == 4:
                # 尝试的第五次都没有成功
                transaction.rollback(save_id)
                return JsonResponse({'res': 7, 'errmsg': '下单失败2'})
        ```
  
- 订单支付
    - 支付宝接口调用
    ```
    app_private_key_string = open(os.path.join(settings.BASE_DIR, 'apps/order/app_private_key.pem')).read()
    alipay_public_key_string = open(os.path.join(settings.BASE_DIR, 'apps/order/app_private_key.pem')).read()
    alipay = AliPay(
        appid="支付宝沙箱不可用...",
        app_notify_url=None,  # 默认回调url,不传　不能写空
        app_private_key_string=app_private_key_string,
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True,  # 默认False,True　访问沙箱
    )
    ```  
   - 支付js
    ```
    <script>
        $('.oper_btn').click(function () {
            // 获取status
            statuss = $(this).attr('status')
            if (statuss == 1) {
                // 进行支付
                // 获取订单id
                order_id = $(this).attr('order_id')
                csrf = $('input[name="csrfmiddlewaretoken"]').val()
                // 组织参数
                params = {'order_id': order_id, 'csrfmiddlewaretoken': csrf}
                // 发起Ajax post请求 访问/order/pay, 传递参数order_id, 返回data
                $.post('/order/pay', params, function (data) {
                    // 状态判断
                    if (data.res == 3) {
                        // 引导用户到支付页面
                        window.open(data.pay_url)
                        //  21:44:17]"POST /order/pay HTTP/1.1" 200 930

                    } else {
                        alert(data.errmsg)
                    }
                })

            } else {
                // 其他情况
            }
        })
    </script>

    ```

## 项目部署
- uwsgi
    - uwsgi配置　　
    ```
    DEBUG=FALSE
    ALLOWED_HOSTS=[‘*’] 
    ```
    - uwsgi.ini  
    ```
    [uwsgi]
    #使用nginx连接时使用
    socket=127.0.0.1:8080
    #直接做web服务器使用 = python manage.py runserver ip:port
    ;http=127.0.0.1:8080
    #项目目录
    chdir=/home/huxf/Dj18/dailyfresh
    #项目中wsgi.py文件的目录，相对于项目目录
    wsgi-file=dailyfresh/wsgi.py
    # 指定启动的工作进程数 4()
    processes=4
    # 指定启动的工作进程中的线程数
    threads=2
    # 主进程
    master=True
    # 保存启动后的主进程的pid进程号
    pidfile=uwsgi.pid
    # 设置uwsgi后台运行,uwsgi.log保存日志信息
    daemonize=uwsgi.log
    # 设置虚拟环境的路径
    virtualenv=/home/huxf/.pyenv/versions/dj182

    ```
    - nginx 转发请求给uwsgi
    ```
    location / {
	include uwsgi_params;
	uwsgi_pass uwsgi服务器的ip:port;
    }
    ```
   - 收集静态文件
   `python manage.py collectstatic`  
## 注意点
redis版本需要2.10.6 否则会报错,因为使用django的版本(1.8.2)过低问题  
如果使用乐观锁,需要修改mysql事务的隔离级别设置

## 总结

## 项目展示
![首页](https://github.com/HuXifan/Dailyfresh/raw/master/static/images/README_iamges/index.png)
![购物车](https://github.com/HuXifan/Dailyfresh/raw/master/static/images/README_iamges/cart.png)
![用户中心](https://github.com/HuXifan/Dailyfresh/raw/master/static/images/README_iamges/user_center.png) 
![订单](https://github.com/HuXifan/Dailyfresh/raw/master/static/images/README_iamges/order.png)
## 项目布局
```
  ├── apps
│   ├── cart
│   │   ├── admin.py
│   │   ├── __init__.py
│   │   ├── migrations
│   │   │   ├── __init__.py
│   │   │   └── __pycache__
│   │   │       └── __init__.cpython-35.pyc
│   │   ├── models.py
│   │   ├── __pycache__
│   │   │   ├── admin.cpython-35.pyc
│   │   │   ├── __init__.cpython-35.pyc
│   │   │   ├── __init__.cpython-37.pyc
│   │   │   ├── models.cpython-35.pyc
│   │   │   ├── urls.cpython-35.pyc
│   │   │   └── views.cpython-35.pyc
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── goods
│   │   ├── admin.py
│   │   ├── __init__.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   ├── __init__.py
│   │   │   └── __pycache__
│   │   │       ├── 0001_initial.cpython-35.pyc
│   │   │       └── __init__.cpython-35.pyc
│   │   ├── models.py
│   │   ├── __pycache__
│   │   │   ├── admin.cpython-35.pyc
│   │   │   ├── __init__.cpython-35.pyc
│   │   │   ├── __init__.cpython-37.pyc
│   │   │   ├── models.cpython-35.pyc
│   │   │   ├── search_indexes.cpython-35.pyc
│   │   │   ├── urls.cpython-35.pyc
│   │   │   └── views.cpython-35.pyc
│   │   ├── search_indexes.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── __init__.py
│   ├── order
│   │   ├── admin.py
│   │   ├── alipay_public_key.pem
│   │   ├── app_private_key.pem
│   │   ├── __init__.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   ├── 0002_auto_20191105_1131.py
│   │   │   ├── __init__.py
│   │   │   └── __pycache__
│   │   │       ├── 0001_initial.cpython-35.pyc
│   │   │       ├── 0002_auto_20191105_1131.cpython-35.pyc
│   │   │       └── __init__.cpython-35.pyc
│   │   ├── models.py
│   │   ├── __pycache__
│   │   │   ├── admin.cpython-35.pyc
│   │   │   ├── __init__.cpython-35.pyc
│   │   │   ├── __init__.cpython-37.pyc
│   │   │   ├── models.cpython-35.pyc
│   │   │   ├── urls.cpython-35.pyc
│   │   │   └── views.cpython-35.pyc
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── __pycache__
│   │   └── __init__.cpython-35.pyc
│   └── user
│       ├── admin.py
│       ├── __init__.py
│       ├── migrations
│       │   ├── 0001_initial.py
│       │   ├── __init__.py
│       │   └── __pycache__
│       │       ├── 0001_initial.cpython-35.pyc
│       │       └── __init__.cpython-35.pyc
│       ├── models.py
│       ├── __pycache__
│       │   ├── admin.cpython-35.pyc
│       │   ├── __init__.cpython-35.pyc
│       │   ├── __init__.cpython-37.pyc
│       │   ├── models.cpython-35.pyc
│       │   ├── urls.cpython-35.pyc
│       │   └── views.cpython-35.pyc
│       ├── tests.py
│       ├── urls.py
│       └── views.py
├── celery_tasks
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-35.pyc
│   │   └── tasks.cpython-35.pyc
│   └── tasks.py
├── dailyfresh
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-35.pyc
│   │   ├── __init__.cpython-37.pyc
│   │   ├── settings.cpython-35.pyc
│   │   ├── settings.cpython-37.pyc
│   │   ├── urls.cpython-35.pyc
│   │   ├── urls.cpython-37.pyc
│   │   └── wsgi.cpython-35.pyc
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── db
│   ├── base_model.py
│   ├── __init__.py
│   └── __pycache__
│       ├── base_model.cpython-35.pyc
│       └── __init__.cpython-35.pyc
├── demo.html
├── dump.rdb
├── fdfs_demo.py
├── manage.py
├── __pycache__
│   └── manage.cpython-35.pyc
├── README.md
├── requirement.txt
├── static
├── static_root
├── templates
│   ├── base_detail_list.html
│   ├── base.html
│   ├── base_no_cart.html
│   ├── base_user_center.html
│   ├── cart.html
│   ├── detail.html
│   ├── index.html
│   ├── __init__.py
│   ├── list.html
│   ├── login.html
│   ├── place_order6.html
│   ├── place_order.html
│   ├── register.html
│   ├── search
│   │   ├── indexes
│   │   │   └── goods
│   │   │       └── goodssku_text.txt
│   │   ├── search1.html
│   │   └── search.html
│   ├── static_base.html
│   ├── static_index.html
│   ├── user_center_info.html
│   ├── user_center_order.html
│   └── user_center_site.html
├── utils
│   ├── fdfs
│   │   ├── client.conf
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-35.pyc
│   │   │   └── storage.cpython-35.pyc
│   │   └── storage.py
│   ├── __init__.py
│   ├── mixin.py
│   └── __pycache__
│       ├── __init__.cpython-35.pyc
│       └── mixin.cpython-35.pyc
├── uwsgi2.ini
├── uwsgi2.log
├── uwsgi2.pid
├── uwsgi.ini
├── uwsgi.log
├── uwsgi.pid
└── whoosh_index
    ├── _MAIN_21.toc
    ├── MAIN_vedvannehnv0pkzh.seg
    └── MAIN_WRITELOCK

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