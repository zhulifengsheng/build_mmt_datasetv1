from django.db import models

# 创建数据库
# create database mmt_databasev1 DEFAULT CHARSET utf8 COLLATE utf8_general_ci;

# 执行创建数据库表的命令
# python3 manage.py makemigrations
# python3 manage.py migrate

# 特殊情况的处理方法
# alter table annotation_caption auto_increment 1;
# python3 manage.py makemigrations --empty annotation

_MAX = 10000    # 计划标注1W张图片

class RandomImageID(models.Model):
    '''
    给123287张图片随机打乱顺序
    '''
    Random_imageID_id = models.BigAutoField(verbose_name='Random_imageID ID', primary_key=True)
    image_id = models.PositiveIntegerField(verbose_name='图片id', unique=True)

class Image(models.Model):
    image_id = models.BigAutoField(verbose_name='图片ID', primary_key=True)
    image_name = models.CharField(verbose_name='图片名字', max_length=34, unique=True)

class User(models.Model):
    # lch lv12345
    username = models.CharField(verbose_name='用户名', max_length=5, primary_key=True)  # 用户名不能重复
    password = models.CharField(verbose_name='密码', max_length=10)
    
    # 不看图片标注（与caption_id对应）
    now_index_without_image = models.PositiveIntegerField(verbose_name='该标注哪个了', default=1)    # 没有被分配过任务时，初始化为0
    total_amount_without_image = models.PositiveIntegerField(verbose_name='标注的总量', default=0)
    
    # 看图片标注（与zh_without_image_id对应）
    now_index_with_image = models.PositiveIntegerField(verbose_name='该标注哪个了', default=1)    # 没有被分配过任务时，初始化为0
    total_amount_with_image = models.PositiveIntegerField(verbose_name='标注的总量', default=0)
    
    is_admin = models.BooleanField(verbose_name='是否是管理员', default=False)

class FirstStageWorkPool(models.Model):
    '''
    第一阶段工作池，根据_MAX最大标注的图片数量，这个第一阶段任务的标注数量也会是固定的
    '''
    # 默认主键id
    caption_obj = models.ForeignKey(to="Caption", to_field="caption_id", on_delete=models.CASCADE)
    user_obj = models.ForeignKey(to="User", to_field="username", on_delete=models.SET_NULL, null=True)  # 那个用户对该英文描述进行不看图片译文标注
    is_finished = models.BooleanField(verbose_name='这个标注是否完成了', default=False)

class Caption(models.Model):
    caption_id = models.BigAutoField(verbose_name='Caption ID', primary_key=True)
    caption_NO = models.PositiveSmallIntegerField(verbose_name='第几个描述')    # 1-7
    caption = models.TextField(verbose_name='英文描述')
    zh_machine_translation = models.TextField(verbose_name='机器翻译')
    is_ambiguity = models.BooleanField(verbose_name='改英文是否歧义', default=False)

    # 该caption链接到那个图片
    image_obj = models.ForeignKey(to="Image", to_field="image_id", on_delete=models.CASCADE)    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['image_obj', 'caption_NO'], name="this_caption_of_this_image"),
        ]

class ZhWithoutImage(models.Model):
    zh_without_image_id = models.BigAutoField(verbose_name='ZhWithoutImage ID', primary_key=True)
    zh_without_image = models.TextField(verbose_name='不看图片标注的中文')

    # 该不看图片中文链接到那个Caption
    caption_obj = models.ForeignKey(to="Caption", to_field="caption_id", on_delete=models.CASCADE)
    # 谁标注的这个不看图片中文
    user_that_annots_it = models.ForeignKey(to="User", to_field="username", on_delete=models.SET_NULL, null=True)
