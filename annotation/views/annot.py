from django.shortcuts import render, redirect
from django.http import Http404

from annotation.models import FirstStageWorkPool, User, ZhWithoutImage

def annotation_without_image(request, index_without_image):
    '''
    只可以访问当前要标注的数据 和 之前标注过的数据
    '''
    if request.session.get("info") is None or 'username' not in request.session.get("info"):
        raise Http404("非法访问")
    
    # 找到用户要标注的那个caption_id
    user_obj = User.objects.get(username=request.session.get("info")['username'])
    
    # 不可以访问超过标注总量的页面
    if user_obj.total_amount_without_image < index_without_image:
        return redirect('/annotation_without_image/{}/'.format(user_obj.now_index_without_image))
    # 不可以超前访问待标注的数据
    if user_obj.now_index_without_image < index_without_image:
        return redirect('/annotation_without_image/{}/'.format(user_obj.now_index_without_image))
    
    # 传递到前端的参数
    caption_obj = FirstStageWorkPool.objects.get(user_obj=user_obj.username, index_without_image=index_without_image).caption_obj
    qiyi = False
    zh1, zh2 = caption_obj.zh_machine_translation, ''   # 找到之前标注过的中文
    zhwithoutimage = ZhWithoutImage.objects.filter(caption_obj=caption_obj, user_that_annots_it=user_obj).order_by('zh_without_image_id')
    if zhwithoutimage.exists():
        zhs = [i.zh_without_image for i in zhwithoutimage] + ['']
        zh1 = zhs[0]
        zh2 = zhs[1]
        if zh2 != '':
            qiyi = True

    res = {
        'annotated_amount': index_without_image, # 已标注的个数
        'zh1': zh1,
        'zh2': zh2,
        'total': user_obj.total_amount_without_image,   # 总共需要标注的个数
        'caption_id': caption_obj.caption_id,
        'caption': caption_obj.caption,
        'zh_machine_translation': caption_obj.zh_machine_translation,
        'is_admin': user_obj.is_admin,
        'qiyi': qiyi,   # 是否是歧义句
    }
    return render(request, 'annotation_without_image.html', res)