# 定义索引类
from haystack import indexes
# 导入模型类
from goods.models import GoodsSKU


# 指定对于某个类的某些数据建立索引 模型类名+Index
class GoodsSKUIndex(indexes.SearchIndex, indexes.Indexable):
    # 索引字段，use_template=True 指定表中哪些字段建立索引数据，把说明放在一个文件（templates/search/indexes/goods里面）中
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return GoodsSKU  # 返回模型类

    # 建立索引数据
    def index_queryset(self, using=None):
        return self.get_model().objects.all()
