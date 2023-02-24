from annotation.models import (
    RandomImageID, 
    _MAX, 
    Caption, 
    Image, 
    FirstStageWorkPool, 
    ZhWithoutImage, 
    SecondStageWorkPool,
    ZhWithImage,
    FixInfo,
)
from annotation.utils.backend import (
    get_total_amount_with_image,
    get_total_amount_without_image,
)

# 给用户删除任务量
def util_management_del(task, user_obj, num):
    if task == 'first':
        total_amount_without_image = get_total_amount_without_image(user_obj)
        if total_amount_without_image - user_obj.now_index_without_image + 1 < num:
            # 删除的任务量大于未标注的任务量
            return False
        else:
            # 删除工作池中已分配的任务
            for i in range(num):
                FirstStageWorkPool.objects.filter(user_obj=user_obj, index_without_image=total_amount_without_image-i).delete()
    
    else:
        total_amount_with_image = get_total_amount_without_image(user_obj)
        if total_amount_with_image - user_obj.now_index_with_image + 1 < num:
            # 删除的任务量大于未标注的任务量
            return False
        else:
            # 删除工作池中已分配的任务
            for i in range(num):
                SecondStageWorkPool.objects.filter(user_obj=user_obj, index_with_image=total_amount_with_image-i).delete()

    return True

# 给用户添加任务量
def util_management_add(task, user_obj, num):
    if task == 'first':
        # 给用户添加第一阶段的任务
        total_amount_without_image = get_total_amount_without_image(user_obj)

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
                FirstStageWorkPool.objects.create(user_obj=user_obj, caption_obj=caption_obj, index_without_image=total_amount_without_image+t)
                if t == num:
                    # 任务分配完毕
                    break
    
    else:
        # 给用户添加第二阶段的任务
        total_amount_with_image = get_total_amount_with_image(user_obj)

        t = 0 # 记录成功分配的个数
        zhs_without_image = ZhWithoutImage.objects.all()
        __MAX = len(zhs_without_image)

        for i in range(__MAX):   # 从0开始
            zh_without_image_obj = zhs_without_image[i]
            
            if SecondStageWorkPool.objects.filter(zh_without_image_obj=zh_without_image_obj).exists():
                # 该不看图片译文已分配到某用户的任务中
                continue
            else:
                t += 1
                SecondStageWorkPool.objects.create(user_obj=user_obj, zh_without_image_obj=zh_without_image_obj, index_with_image=total_amount_with_image+t)
                if t == num:
                    # 任务分配完毕
                    break
    
    return t

# 创建不看图片标注中文
def create_zh_without_image(zh, caption_obj, user_obj):
    ZhWithoutImage.objects.create(zh_without_image=zh, caption_obj=caption_obj, user_that_annots_it=user_obj)

# 更新不看图片标注中文
def update_zh_without_image(zh_without_image_obj, user_obj, zh):
    ZhWithoutImage.objects.filter(zh_without_image_obj_id=zh_without_image_obj.id).update(zh_without_image=zh)

    # 找到该不看图片标注中文级联的看图片标注中文，并将其删除（如不存在级联的看图片标注中文，此语句什么都不会执行）
    ZhWithImage.objects.filter(user_that_annots_it=user_obj, zh_without_image_obj=zh_without_image_obj).delete()

    t = SecondStageWorkPool.objects.filter(zh_without_image_obj=zh_without_image_obj)
    # 如果该不看图片标注中文已被添加到第二阶段的标注任务中，需要对其重新标注
    if t.exists():
        t.update(is_finished=False)

'''TODO'''
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
