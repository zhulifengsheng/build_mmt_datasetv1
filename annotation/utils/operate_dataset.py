from annotation.models import (
    User, 
    RandomImageID, 
    _MAX, 
    Caption, 
    Image, 
    FirstStageWorkPool, 
    ZhWithoutImage, 
    SecondStageWorkPool,
    ZhWithImage,
    FixInfo
)

# 给用户删除任务量
def util_management_del(username, task, user_obj, num):
    if task == 'first':
        if user_obj.total_amount_without_image - user_obj.now_index_without_image + 1 < num:
            return False
        else:
            User.objects.filter(username=username).update(total_amount_without_image=user_obj.total_amount_without_image-num)
            # 删除工作池中已分配的任务
            for i in range(num):
                FirstStageWorkPool.objects.filter(user_obj=user_obj, index_without_image=user_obj.total_amount_without_image-i).delete()
    else:
        if user_obj.total_amount_with_image - user_obj.now_index_with_image + 1 < num:
            return False
        else:
            User.objects.filter(username=username).update(total_amount_with_image=user_obj.total_amount_with_image-num)
            # 删除工作池中已分配的任务
            for i in range(num):
                SecondStageWorkPool.objects.filter(user_obj=user_obj, index_with_image=user_obj.total_amount_with_image-i).delete()

    return True

# 给用户添加任务量
def util_management_add(username, task, user_obj, num):
    if task == 'first':
        # 给用户添加第一阶段的任务
        t = 0   # 记录成功分配的个数
        for i in range(1, _MAX+1):
            image_id = RandomImageID.objects.get(Random_imageID_id=i).image_id
            image_obj = Image.objects.get(image_id=image_id)
            caption_obj = Caption.objects.get(image_obj=image_obj, caption_NO=1)
            
            if FirstStageWorkPool.objects.filter(caption_obj=caption_obj).exists():
                # 该看图片译文已分配到某用户的任务中
                continue
            else:
                t += 1
                FirstStageWorkPool.objects.create(user_obj=user_obj, caption_obj=caption_obj, index_without_image=user_obj.total_amount_without_image+t)
                if t == num:
                    # 任务分配完毕
                    break
        # 更新总任务量
        User.objects.filter(username=username).update(total_amount_without_image=user_obj.total_amount_without_image+t)
    
    else:
        # 给用户添加第二阶段的任务
        t = 0 # 记录成功分配的个数
        __MAX = len(ZhWithoutImage.objects.all())
        zhs_without_image = ZhWithoutImage.objects.all()

        for i in range(__MAX):   # 从0开始
            zh_without_image_obj = zhs_without_image[i]
            if SecondStageWorkPool.objects.filter(zh_without_image_obj=zh_without_image_obj).exists():
                # 该不看图片译文已分配到某用户的任务中
                continue
            else:
                t += 1
                SecondStageWorkPool.objects.create(user_obj=user_obj, zh_without_image_obj=zh_without_image_obj, index_with_image=user_obj.total_amount_with_image+t)
                if t == num:
                    # 任务分配完毕
                    break
        # 更新总任务量
        User.objects.filter(username=username).update(total_amount_with_image=user_obj.total_amount_with_image+t)  
    
    return t

# 创建第一阶段数据
def create_zh_without_image(zh, caption_obj, user_obj):
    ZhWithoutImage.objects.create(zh_without_image=zh, caption_obj=caption_obj, user_that_annots_it=user_obj)

# 更新已标注过的第一阶段数据
def update_zh_without_image(zh, caption_obj, user_obj, index):
    '''
        说明：对不看图片标注的译文来说，更新的同时还需要对其链接的看图片标注进行删除
    '''
    # 先通过 caption_obj 和 user_obj 找到数据，然后进行修改
    zhs = ZhWithoutImage.objects.filter(caption_obj=caption_obj, user_that_annots_it=user_obj).order_by('zh_without_image_id')
    
    id = zhs[index].zh_without_image_id
    ZhWithoutImage.objects.filter(zh_without_image_id=id).update(zh_without_image=zh)
    
    # 找到其链接的看图片标注中文，并将其删除
    zh_without_image_obj = ZhWithoutImage.objects.get(zh_without_image_id=id)
    ZhWithImage.objects.filter(user_that_annots_it=user_obj, zh_without_image_obj=zh_without_image_obj).delete()

# 删除已标注过的第一阶段数据（只会对第二个标注的中文进行删除操作）
def del_zh_without_image(caption_obj, user_obj):
    '''
        说明：如果第二个标注存在则删除它，若不存在则不执行
    '''
    zhs = ZhWithoutImage.objects.filter(caption_obj=caption_obj, user_that_annots_it=user_obj).order_by('zh_without_image_id')
    if len(zhs) != 1:
        id = zhs[1].zh_without_image_id
        ZhWithoutImage.objects.filter(zh_without_image_id=id).delete()

# 创建第二阶段数据
def create_zh_with_image(zh, user_obj, zh_without_image_obj):
    ZhWithImage.objects.create(zh_with_image=zh, zh_without_image_obj=zh_without_image_obj, user_that_annots_it=user_obj)
    return ZhWithImage.objects.get(zh_without_image_obj=zh_without_image_obj, user_that_annots_it=user_obj)

# 删除已标注过的第二阶段数据
def del_zh_with_image_and_fixinfos(user_obj, zh_without_image_obj):
    # 先删除修正信息，再删除中文
    zh_with_image_obj = ZhWithImage.objects.get(user_that_annots_it=user_obj, zh_without_image_obj=zh_without_image_obj)
    FixInfo.objects.filter(zh_with_image_obj=zh_with_image_obj).delete()
    ZhWithImage.objects.filter(user_that_annots_it=user_obj, zh_without_image_obj=zh_without_image_obj).delete()

# 创建修正信息
dic_error_choices = {
    '名词': 1,
    '动词': 2,
    '形容词': 3,
    '数量': 4,
    '细化': 5,
}
def create_fix_info(old_words, old_words_pos, new_words, new_words_pos, type_list, zh_with_image_obj):
    '''
        args:   old_words：修正之前单词的列表
                old_words_pos：修正之前单词在旧中文中的位置，元素是元组，表示开始和结束位置（左闭右开区间）
                new_words：修正之后单词的列表
                new_words_pos：修正之后单词在新中文中的位置，元素是元组，表示开始和结束位置（左闭右开区间）
                type_list：修正类型列表
                zh：修正之后的中文
    '''
    for old_word, old_word_pos, new_word, new_word_pos, type in zip(old_words, old_words_pos, new_words, new_words_pos, type_list):
        FixInfo.objects.create(word_before_change=old_word, word_after_change=new_word, word_before_change_start_pos=old_word_pos[0], word_before_change_end_pos=old_word_pos[1], word_after_change_start_pos=new_word_pos[0], word_after_change_end_pos=new_word_pos[1], which_classification=dic_error_choices[type], zh_with_image_obj=zh_with_image_obj)
