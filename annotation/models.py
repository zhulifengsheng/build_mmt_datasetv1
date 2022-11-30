from django.db import models

# create database mmt_databasev1 DEFAULT CHARSET utf8 COLLATE utf8_general_ci;
# python3 manage.py makemigrations --empty annotation
# python3 manage.py makemigrations
# python3 manage.py migrate

# alter table annotation_caption1 auto_increment 1;

# Create your models here.

class Image(models.Model):
    # id
    image_name = models.CharField(verbose_name='图片名字', max_length=34, unique=True)

class User(models.Model):
    # lch lv12345
    username = models.CharField(verbose_name='用户名', max_length=5, primary_key=True)
    password = models.CharField(verbose_name='密码', max_length=10)
    
    # 不看图片标注（与caption_id对应）
    now_index_without_image = models.PositiveIntegerField(verbose_name='该标注哪个了', default=0)    # 没有被分配过任务时，初始化为0
    total_amount_without_image = models.PositiveSmallIntegerField(verbose_name='计划标注的总量', default=0)
    start_index_without_image = models.PositiveIntegerField(verbose_name='从哪个开始标注', default=1)

    # 看图片标注（与zh_without_image_id对应）
    now_index_with_image = models.PositiveIntegerField(verbose_name='该标注哪个了', default=0)    # 没有被分配过任务时，初始化为0
    total_amount_with_image = models.PositiveSmallIntegerField(verbose_name='计划标注的总量', default=0)
    start_index_with_image = models.PositiveIntegerField(verbose_name='从哪个开始标注', default=1)
    is_admin = models.BooleanField(verbose_name='是否是管理员', default=False)

class Caption(models.Model):
    # id
    caption_NO = models.PositiveSmallIntegerField(verbose_name='第几个描述')    # 1-7
    caption = models.TextField(verbose_name='英文描述')
    zh_machine_translation = models.TextField(verbose_name='机器翻译')

class ZhWithoutImage(models.Model):
    pass