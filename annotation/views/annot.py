from django.shortcuts import render, redirect
from django.http import Http404

from annotation.models import FirstStageWorkPool, User, ZhWithoutImage, SecondStageWorkPool, ZhWithImage, FixInfo
from annotation.utils.backend import image_url, html_zh

def annotation_without_image(request, index_without_image):
    '''
    只可以访问当前要标注的数据 和 之前标注过的数据
    '''
    if request.session.get("info") is None or 'username' not in request.session.get("info"):
        raise Http404("非法访问")

    user_obj = User.objects.get(username=request.session.get("info")['username'])
    
    # 不可以访问超过标注总量的页面，不可以超前访问待标注的数据
    if user_obj.total_amount_without_image < index_without_image or user_obj.now_index_without_image < index_without_image:
        index = min(user_obj.now_index_without_image, user_obj.total_amount_without_image)
        return redirect('/annotation_without_image/{}/'.format(index))
    
    # 传递到前端的参数
    caption_obj = FirstStageWorkPool.objects.get(user_obj=user_obj, index_without_image=index_without_image).caption_obj
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

def annotation_with_image(request, index_with_image):
    '''
    只可以访问当前要标注的数据 和 之前标注过的数据
    '''
    if request.session.get("info") is None or 'username' not in request.session.get("info"):
        raise Http404("非法访问")
    
    user_obj = User.objects.get(username=request.session.get("info")['username'])

    # 不可以访问超过标注总量的页面，不可以超前访问待标注的数据
    if user_obj.total_amount_with_image < index_with_image or user_obj.now_index_with_image < index_with_image:
        index = min(user_obj.now_index_with_image, user_obj.total_amount_with_image)
        return redirect('/annotation_with_image/{}/'.format(index))
    
    # 传递到前端的参数
    zh_without_image_obj = SecondStageWorkPool.objects.get(user_obj=user_obj, index_with_image=index_with_image).zh_without_image_obj
    image_obj = zh_without_image_obj.caption_obj.image_obj

    zh = zh_without_image_obj.zh_without_image
    zh_with_image_obj = ZhWithImage.objects.filter(zh_without_image_obj=zh_without_image_obj, user_that_annots_it=user_obj)
    if zh_with_image_obj.exists():
        zh = zh_with_image_obj.first().zh_with_image
        # 找到修正信息，并进行HTML渲染
        fix_infos = FixInfo.objects.filter(zh_with_image_obj=zh_with_image_obj.first())
        zh = html_zh(zh, fix_infos)
    
    res = {
        'annotated_amount': index_with_image, # 已标注的个数
        'image_name': image_url(image_obj.image_name),
        'is_admin': user_obj.is_admin,
        'total': user_obj.total_amount_with_image,
        'zh_without_image': zh_without_image_obj.zh_without_image,
        'zh': zh,
    }
    return render(request, 'annotation_with_image.html', res)