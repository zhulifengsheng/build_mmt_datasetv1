from django.shortcuts import render

from annotation.models import Image, Caption

def annotation_without_image(request, caption_id):
    # 找到用户要标注的那个caption_id
    Caption_obj = Caption.objects.get(caption_id=caption_id)
    res = {
        'caption_id': caption_id,
        # 已标注的个数
        'annotated_amount': 12,
        # 总共需要标注的个数
        'total': 300,
        'caption': Caption_obj.caption,
        'zh_machine_translation': Caption_obj.zh_machine_translation,
    }
    return render(request, 'annotation_without_image.html', res)