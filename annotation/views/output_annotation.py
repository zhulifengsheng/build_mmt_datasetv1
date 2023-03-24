from django.http import Http404
from django.shortcuts import render, HttpResponse
import json
from annotation.models import User, ZhWithImage, FixInfo

error_choices = {
    1: '名词',
    2: '动词',
    3: '形容词',
    4: '数量',
    5: '细化',
}

def output_annotation(request):
    # with open('annotation.json', 'r') as f:
    #     data = json.load(f)
    # print(data)

    # 输出标注信息
    t = {}

    for i in ZhWithImage.objects.all():
        zh_without_image_obj = i.zh_without_image_obj   # 对应的不看图片标注的中文对象
        caption_obj = zh_without_image_obj.caption_obj  # 对应的caption对象

        t[caption_obj.image_obj.image_name] = {
            # '图片名字': ,
            '英文描述': caption_obj.caption,
            '机器翻译': caption_obj.zh_machine_translation,
            '是否歧义': '是' if caption_obj.is_ambiguity else '否',
            '译文': [],
        }
    
    for i in ZhWithImage.objects.all():
        zh_with_image = i.zh_with_image
        zh_without_image_obj = i.zh_without_image_obj   # 对应的不看图片标注的中文对象
        zh_without_image = zh_without_image_obj.zh_without_image
        caption_obj = zh_without_image_obj.caption_obj  # 对应的caption对象

        fix_list = []
        fixinfos = FixInfo.objects.filter(zh_with_image_obj=i)
        if fixinfos.exists():
            for j in fixinfos:
                fix_list.append({
                    '修正之前的词': j.word_before_change,
                    '修正之后的词': j.word_after_change,
                    '修正之前的词的位置区间': (j.word_before_change_start_pos, j.word_before_change_end_pos),
                    '修正之后的词的位置区间': (j.word_after_change_start_pos, j.word_after_change_end_pos),
                    '标注类型': error_choices[j.which_classification]
                })
        
        t[caption_obj.image_obj.image_name]['译文'].append({
            '不看图片标注的中文': zh_without_image,
            '看图片标注的中文': zh_with_image,
            '修正标注信息列表': fix_list,
        })
    
    res = []
    for k, v in t.items():
        v['图片名字'] = k
        res.append(v)
    
    with open('annotation.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False)

    return HttpResponse("信息输出完毕")