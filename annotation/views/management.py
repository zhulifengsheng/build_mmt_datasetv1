from django.shortcuts import render
from django.http import Http404

from annotation.models import User, Caption

def management(request):

    # f1 = open('D:\\LEARN\\datasets\\COCO2017\\captions.txt', 'r', encoding='utf-8')
    # f2 = open('D:\\LEARN\\datasets\\COCO2017\\captions_translation.txt', 'r', encoding='utf-8')
    # for l1, l2 in zip(f1, f2):
    #     # caption_id = models.PositiveIntegerField(verbose_name='Caption ID', primary_key=True)
    #     # caption_NO = models.PositiveSmallIntegerField(verbose_name='第几个描述')    # 1-7
    #     # caption = models.TextField(verbose_name='英文描述')
    #     # zh_machine_translation = models.TextField(verbose_name='机器翻译')
    #     # is_ambiguity = models.BooleanField(verbose_name='改英文是否歧义', default=False)

    #     # # 该caption链接到那个图片
    #     # image_obj = models
    #     Caption.objects.create()
    #     print(l1, l2)
    #     break

    user_obj = User.objects.filter(username=request.session.get("info")['username']).first()
    if user_obj.is_admin:
        # 只有管理员用户才能看见该网页
        return render(request, 'management.html')
    
    return Http404("非法访问")