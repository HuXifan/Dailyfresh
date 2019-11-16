from django.core.files.storage import Storage
from django.conf import settings
from fdfs_client.client import Fdfs_client


class FDFSStorage(Storage):
    # 自定义存储类Fdfs文件存储类

    def __init__(self, client_conf=None, base_url=None):
        # client_conf:指定配置文件路径,域名base_url
        # 初始化
        if client_conf is None:
            client_conf = settings.FDFS_CLIENT_CONF
            # client_conf = './utils/fdfs/client.conf'
        self.client_conf = client_conf
        if base_url is None:
            # base_url = "http://10.10.21.29:8888"
            base_url = settings.FDFS_URL  # 直接从配置文件里拿
        self.base_url = base_url

    def _open(self, name, mode='rb'):
        # 打开文件时使用
        pass

    def _save(self, name, content):
        # 保存文件时使用,上传到FDFS
        # name:上传文件名字, content:包含你上传文件内容的File类的对象, max_length

        # 更改,上传到FDFS

        # 创建Fdfs_client对象
        client = Fdfs_client(self.client_conf)

        # 上传文件到Fdfs系统中
        res = client.upload_by_buffer(content.read())  # 返回字典dict,content.read()方法读取文件内容
        '''
        @return dict {
            'Group name'      : group_name,
            'Remote file_id'  : remote_file_id,
            'Status'          : 'Upload successed.',
            'Local file name' : '',
            'Uploaded size'   : upload_size,
            'Storage IP'      : storage_ip
        } if success else None
        '''
        if res.get('Status') != 'Upload successed.':
            # 上传失败抛出异常
            raise Exception('上传文件到FastDFS失败')
        # 成功,获取返回的文件id
        filename = res.get('Remote file_id')
        # 应该返回被保存文件的真实名称（通常是传进来的<t0>name</t0>，但是如果储存需要修改文件名称，则返回新的名称来代替）。
        return filename

    def exists(self, name):
        '''如果提供的名称所引用的文件在文件系统中存在，则返回True，
        否则如果这个名称可用于新文件，返回False。'''
        # Django判断文件名是否可用,文件内容没有保存到Django服务器,故文件名存在不可用状态
        return False

    def url(self, name):
        # 返回访问文件的url路径
        '''subclasses of Storage must provide a url() method'''
        return self.base_url + name
