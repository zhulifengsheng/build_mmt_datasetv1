from django.shortcuts import render
from django.http import Http404

from annotation.models import Image, Caption, FirstStageWorkPool, User

def annotation_without_image(request, index_without_image):
    if request.session.get("info") is None or 'username' not in request.session.get("info"):
        raise Http404("非法访问")
    
    # 找到用户要标注的那个caption_id
    user_obj = User.objects.get(username=request.session.get("info")['username'])
    x = FirstStageWorkPool.objects.filter(user_obj=user_obj.username).order_by("id")

    Caption_obj = x[index_without_image-1].caption_obj
    res = {
        'annotated_amount': user_obj.now_index_without_image-1, # 已标注的个数
        'total': user_obj.total_amount_without_image,   # 总共需要标注的个数
        'caption_id': Caption_obj.caption_id,
        'caption': Caption_obj.caption,
        'zh_machine_translation': Caption_obj.zh_machine_translation,
    }
    return render(request, 'annotation_without_image.html', res)