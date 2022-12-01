from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import redirect
from annotation.models import User, Caption

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
        caption_objs = Caption.objects.filter(image_obj_id=image_id).order_by('caption_NO')
        data = []
        for caption_obj in caption_objs:
            dic = {}
            dic['zh_machine_translation'] = caption_obj.zh_machine_translation  # 机器翻译
            
            # TODO
            dic['zh_without_image'] = '未标注'
            dic['zh_with_image'] = 'TODO'

            dic['id'] = caption_obj.caption_NO
            data.append(dic)

        context = {
            'code': 0,
            'data': data,
        }
        return JsonResponse(context)

    raise Http404("非ajax访问了该api")

def show_en_table(request):
    if request.is_ajax() and request.method == 'POST':
        image_id = int(request.POST.get('image_id'))
        caption_objs = Caption.objects.filter(image_obj_id=image_id).order_by('caption_NO')
        data = []
        for caption_obj in caption_objs:
            dic = {}
            dic['caption'] = caption_obj.caption
            dic['is_ambiguity'] = 1 if caption_obj.is_ambiguity else 0
            dic['id'] = caption_obj.caption_NO
            data.append(dic)
        
        context = {
            'code': 0,
            'data': data,
        }
        return JsonResponse(context)

    raise Http404("非ajax访问了该api")

def to_annotation_without_image(request):
    # 根据用户名找到用户需要标注第几个caption
    user_obj = User.objects.get(username=request.session.get("info")['username'])
    now_index_without_image = user_obj.now_index_without_image
    total_amount_without_image = user_obj.total_amount_without_image

    if now_index_without_image > total_amount_without_image:
        return HttpResponse("您暂时没有不看图片标注译文的任务")
    else:
        return redirect('/annotation_without_image/{}/'.format(now_index_without_image))