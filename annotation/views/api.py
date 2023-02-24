from django.http import Http404, JsonResponse
from django.shortcuts import redirect, HttpResponse
from annotation.models import (
    User,
    Caption,
    FirstStageWorkPool,
    SecondStageWorkPool,
    ZhWithoutImage,
)
from annotation.utils.operate_dataset import (
    util_management_add,
    create_zh_without_image,
    util_management_del,
    create_zh_with_image,
    create_fix_info,
    del_zh_with_image_and_fixinfos,
    update_zh_without_image,
)
from annotation.utils.backend import (
    parse,
    get_total_amount_without_image,
    get_total_amount_with_image,
    get_isnot_finished_amout,
    get_first_isnot_finished_index,
)

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
            
            # TODO 显示已标注过的数据
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

def show_management_table(request):
    if request.is_ajax() and request.method == 'POST':
        user_objs = User.objects.all()
        
        data = []
        for user_obj in user_objs:
            dic = {}
            dic['username'] = user_obj.username
            dic['first1'] = user_obj.now_index_without_image - 1
            dic['first2']  = get_total_amount_without_image(user_obj) - dic['first1']
            dic['second1'] = get_isnot_finished_amout(user_obj)
            dic['second2']  = get_total_amount_with_image(user_obj) - dic['second1']
            data.append(dic)
        
        context = {
            'code': 0,
            'data': data,
        }
        return JsonResponse(context)

    raise Http404("非ajax访问了该api")

# 标注页面路由
def to_annotation_without_image(request):
    # 根据用户名找到用户需要标注第几个caption
    user_obj = User.objects.get(username=request.session.get("info")['username'])
    total_amount_without_image = get_total_amount_without_image(user_obj)
    
    if total_amount_without_image == 0:
        return HttpResponse('您还没有分配过该任务')

    if user_obj.now_index_without_image > total_amount_without_image:
        # 任务都完成了
        return redirect('/annotation_without_image/{}/'.format(total_amount_without_image))
    else:
        # 任务还在做
        return redirect('/annotation_without_image/{}/'.format(user_obj.now_index_without_image))

def to_annotation_with_image(request):
    # 根据用户名找到用户需要标注第几个caption
    user_obj = User.objects.get(username=request.session.get("info")['username'])
    total_amount_with_image = get_total_amount_with_image(user_obj)
    now_index = get_first_isnot_finished_index(user_obj)
    
    if total_amount_with_image == 0:
        return HttpResponse('您还没有分配过该任务')

    if now_index > total_amount_with_image:
        # 任务都完成了
        return redirect('/annotation_with_image/{}/'.format(total_amount_with_image))
    else:
        # 任务还在做
        return redirect('/annotation_with_image/{}/'.format(now_index))

# 接收前端数据进行处理
def get_annotation_without_image(request):
    if request.is_ajax() and request.method == 'POST':
        user_obj = User.objects.get(username=request.session.get("info")['username'])
        username = user_obj.username
        
        # 保存前端标注的不看图片标注数据
        index = int(request.POST.get('index'))  # index表示用户的第几个标注任务
        zh1 = request.POST.get('zh1')
        zh2 = request.POST.get('zh2')
        assert zh1 != '', '标注的第一个译文不能为空'

        # 通过标注任务，找到用户标注的caption
        caption_obj = FirstStageWorkPool.objects.get(user_obj=user_obj, index_without_image=index).caption_obj
        
        if user_obj.now_index_without_image == index:   # 标注的是新的数据
            # 更新当前标注索引
            User.objects.filter(username=username).update(now_index_without_image=index+1)
            
            # 创建不看图片标注的译文
            create_zh_without_image(zh1, caption_obj, user_obj)
            if zh2 != '':
                create_zh_without_image(zh2, caption_obj, user_obj)
                # 更新Caption为有歧义
                caption_obj.is_ambiguity = True
                caption_obj.save()
            
            if index+1 > get_total_amount_without_image(user_obj):
                # 用户已标注完全部数据，finished=True会让页面自动跳转至管理页面
                return JsonResponse({'annotated_amount': str(index), 'finished': True})
            else:
                return JsonResponse({'annotated_amount': str(index+1), 'finished': False})
        
        else:   # 标注的是已标注过的数据
            # 得到之前标注的中文数据
            zhs = ZhWithoutImage.objects.filter(caption_obj=caption_obj, user_that_annots_it=user_obj).order_by('zh_without_image_id')

            # 更新第一个标注的不看图片译文，只有中文不一样才会执行
            if zhs[0].zh_without_image != zh1:
                update_zh_without_image(zhs[0], user_obj, zh1)
            
            # 更新第二个标注的不看图片译文
            if len(zhs) == 1:
                # 之前没有标注第二个翻译，现在才标注第二个翻译
                if zh2 != '':
                    create_zh_without_image(zh2, caption_obj, user_obj)
            else:
                if zh2 == '':
                    # 删除不看图片标注的中文，会级联删除掉第二阶段任务池中的任务 + 对应的看图片标注的中文
                    ZhWithoutImage.objects.filter(zh_without_image_id=zhs[1].zh_without_image_id).delete()
                
                    # 更新Caption为无歧义
                    caption_obj.is_ambiguity = False
                    caption_obj.save()
                else:
                    update_zh_without_image(zhs[1], user_obj, zh2)

            # 修改过去标注过的译文时，不进行页面跳转，前端提交之后还是返回当前页面
            return JsonResponse({'annotated_amount': str(index), 'finished': False})

    raise Http404("非ajax访问了该api")

def get_annotation_with_image(request):
    if request.is_ajax() and request.method == 'POST':
        user_obj = User.objects.get(username=request.session.get("info")['username'])
        
        # 保存前端标注的不看图片标注数据
        index = int(request.POST.get('index'))  # index表示用户的第几个标注任务
        zh = request.POST.get('zh')
        assert zh != '', '标注的译文不能为空'
        
        # 解析中文中的HTML标签
        old_words, old_words_pos, new_words, new_words_pos, type_list, zh = parse(zh)
        
        # 通过标注任务，找到用户的标注那个zh_without_image
        sswp = SecondStageWorkPool.objects.get(user_obj=user_obj, index_with_image=index)
        zh_without_image_obj = sswp.zh_without_image_obj

        # 该数据已标注完了，修改标注记录
        sswp.is_finished = True
        sswp.save()

        # 先delete这个看图片标注的中文和相关修正信息
        del_zh_with_image_and_fixinfos(user_obj, zh_without_image_obj)

        zh_with_image_obj = create_zh_with_image(zh, user_obj, zh_without_image_obj)
        if old_words is not None:
            create_fix_info(old_words, old_words_pos, new_words, new_words_pos, type_list, zh_with_image_obj)

        # 页面跳转
        index = get_first_isnot_finished_index(user_obj)    # 找到下一个未标注的数据
        if index == get_total_amount_with_image(user_obj):
            # 用户已标注完全部数据，finished=True会让页面自动跳转至管理页面
            return JsonResponse({'annotated_amount': str(index), 'finished': True})
        else:
            return JsonResponse({'annotated_amount': str(index), 'finished': False})

    raise Http404("非ajax访问了该api")

# 后台数据管理
def management_del(request):
    if request.is_ajax() and request.method == 'POST':
        num = int(request.POST.get('number'))
        username = request.POST.get('username')
        task = request.POST.get('task')

        error_context = {
            'code': 0,
            'success': False,
        }

        # 1 错误的数字范围报错
        if num <= 0:
            return JsonResponse(error_context)
        
        user_obj = User.objects.filter(username=username)
        # 2 用户不存在报错
        if not user_obj.exists():
            return JsonResponse(error_context)
        user_obj = user_obj.first()

        if task == 'first' or task == 'second':
            if util_management_del(task, user_obj, num) == False:
                return JsonResponse(error_context)
        else:
            # 3 错误的任务标志
            return JsonResponse(error_context)

        return JsonResponse({'code': 0, 'success': True})
    
    raise Http404("非ajax访问了该api")

def management_add(request):
    if request.is_ajax() and request.method == 'POST':
        num = int(request.POST.get('number'))
        username = request.POST.get('username')
        task = request.POST.get('task')

        error_context = {
            'code': 0,
            'success': False,
        }

        # 1 错误的数字范围报错
        if num <= 0 or num > 300:
            return JsonResponse(error_context)
        
        user_obj = User.objects.filter(username=username)
        # 2 用户不存在报错
        if not user_obj.exists():
            return JsonResponse(error_context)
        user_obj = user_obj.first()
        
        if task == 'first' or task == 'second':
            # 如果剩余任务量100，但是分配了300任务量的话，会默认分配完剩下的100任务量并向前端返回分配成功
            t = util_management_add(task, user_obj, num)
            # 一个任务都没有被分配
            if t == 0:
                return JsonResponse(error_context)
        else:
            # 3 错误的任务标志
            return JsonResponse(error_context)

        return JsonResponse({'code': 0, 'success': True})
    
    raise Http404("非ajax访问了该api")