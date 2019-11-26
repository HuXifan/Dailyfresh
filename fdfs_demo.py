from fdfs_client.client import Fdfs_client

client = Fdfs_client('/etc/fdfs/client.conf')
ret = client.upload_by_filename('fdfs_demo.py')
print('__' * 10 + '验证fdfs+nginx服务是否开启成功')
print(ret)
'''
{'Local file name': 'fdfs_demo.py', 'Storage IP': '10.10.21.29', 'Remote file_id': 'group1/M00/00/00/CgoVHV3PsfCAZU9qAAAAtYX8Org2798.py', 'Status': 'Upload successed.', 'Uploaded size': '181B', 'Group name': 'group1'}

'''
print('__' * 10)

# 海量存储,存储容量扩展方便,文件内容重复


