from django.http import Http404, JsonResponse

from annotation.models import User

# finish
def login(request):
    if request.is_ajax() and request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        res = User.objects.filter(username=username, password=password)
        if res.exists():
            # save session
            request.session["info"] = {'username': username}
            is_user = True
        else:   
            is_user = False
        
        context = {
            'is_user': is_user,
            'username': username,
        }
        return JsonResponse(context)

    raise Http404("非ajax访问了该api")

def show_zh_table(request):
    if request.is_ajax() and request.method == 'POST':
        image_id = int(request.POST.get('image_id'))
        # caption_objs = Caption.objects.filter(image_obj_id=image_id).order_by('caption_number')
        data = []
        # for caption_obj in caption_objs:
        #     dic = {}
        #     dic['zh_machine_translation'] = caption_obj.zh_machine_translation  # 机器翻译
        #     if caption_obj.zh_without_image_obj:   # 若有不看图片标注，选择歧义中正确的那个
        #         t = caption_obj.zh_without_image_obj
        #         dic['zh_without_image'] = t.zhs_without_image.split('\n')[t.correct_number]
        #     else:
        #         dic['zh_without_image'] = '未标注'
        #     if caption_obj.fix_zh_with_image_obj:   # 若有看图片标注，更新不看图片标注为fix_zh，它带HTML有更多信息
        #         t = caption_obj.fix_zh_with_image_obj
        #         dic['zh_without_image'] = t.fix_zh_with_image
        #         if t.zh_with_image: # 看图片标注存在
        #             dic['zh_with_image'] = t.zh_with_image
        #     else:
        #         dic['zh_with_image'] = '未标注'
        #     dic['id'] = caption_obj.caption_number
        #     data.append(dic)

        context = {
            'code': 0,
            'data': data,
        }
        return JsonResponse(context)

    raise Http404("非法访问了该api")

def show_en_table(request):
    if request.is_ajax() and request.method == 'POST':
        image_id = int(request.POST.get('image_id'))
        # caption_objs = Caption.objects.filter(image_obj_id=image_id).order_by('caption_number')
        data = []
        # for caption_obj in caption_objs:
        #     dic = {}
        #     dic['caption'] = caption_obj.caption
        #     if caption_obj.zh_without_image_obj and caption_obj.zh_without_image_obj.user_thinks_caption_ambiguity:
        #         dic['is_ambiguity'] = 1
        #     else:
        #         dic['is_ambiguity'] = 0
        #     dic['id'] = caption_obj.caption_number
        #     data.append(dic)
        
        context = {
            'code': 0,
            'data': data,
        }
        return JsonResponse(context)

    raise Http404("非法访问了该api")