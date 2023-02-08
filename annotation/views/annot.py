from django.shortcuts import render, redirect
from django.http import Http404

from annotation.models import FirstStageWorkPool, User, ZhWithoutImage

def annotation_without_image(request, index_without_image):
    # 只可以访问当前要标注的数据 和 之前标注过的数据
    if request.session.get("info") is None or 'username' not in request.session.get("info"):
        raise Http404("非法访问")
    
    # 找到用户要标注的那个caption_id
    user_obj = User.objects.get(username=request.session.get("info")['username'])
    # 不可以超前访问待标注的数据
    if user_obj.now_index_without_image < index_without_image:
        return redirect('/annotation_without_image/{}/'.format(user_obj.now_index_without_image))

    caption_obj = FirstStageWorkPool.objects.get(user_obj=user_obj.username, index_without_image=index_without_image).caption_obj

    # 找到之前标注过的中文
    zhwithoutimage = ZhWithoutImage.objects.filter(caption_obj=caption_obj, user_that_annots_it=user_obj)

    res = {
        'annotated_amount': index_without_image, # 已标注的个数
        # TODO 显示曾经标注过的数据
        # 'zh1'
        # 'zh2'
        'total': user_obj.total_amount_without_image,   # 总共需要标注的个数
        'caption_id': caption_obj.caption_id,
        'caption': caption_obj.caption,
        'zh_machine_translation': caption_obj.zh_machine_translation,
        'is_admin': user_obj.is_admin,
    }
    return render(request, 'annotation_without_image.html', res)