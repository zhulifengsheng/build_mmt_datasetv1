import os
from annotation.models import User, RandomImageID, _MAX, Caption, Image, FirstStageWorkPool, ZhWithoutImage

def image_url(image_name):
    path_list = ['img', 'coco']
    path_list.extend(image_name.split('_'))
    return os.path.join(*path_list)

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
                continue
            else:
                t += 1
                FirstStageWorkPool.objects.create(user_obj=user_obj, caption_obj=caption_obj, index_without_image=user_obj.total_amount_without_image+t)
                if t == num:
                    break
        
        User.objects.filter(username=username).update(total_amount_without_image=user_obj.total_amount_without_image+t)
    else:
        # TODO 给用户添加第二阶段的任务
        User.objects.filter(username=username).update(total_amount_with_image=user_obj.total_amount_with_image+num)    

# 创建第一阶段数据
def create_zh_without_image(zh, caption_obj, user_obj):
    ZhWithoutImage.objects.create(zh_without_image=zh, caption_obj=caption_obj, user_that_annots_it=user_obj)

# 更新已标注过的第一阶段数据
def update_zh_without_image(zh, caption_obj, user_obj, index):
    '''
        index: 0 or 1 表示对第几个译文进行修改
    '''
    # 先通过 caption_obj 和 user_obj 找到数据，然后进行修改
    zhs = ZhWithoutImage.objects.filter(caption_obj=caption_obj, user_that_annots_it=user_obj).order_by('zh_without_image_id')
    
    if len(zhs) == 1 and index == 1:
        # 之前没有标注第二个翻译，现在才标注第二个翻译
        create_zh_without_image(zh, caption_obj, user_obj)
    else:
        id = zhs[index].zh_without_image_id
        ZhWithoutImage.objects.filter(zh_without_image_id=id).update(zh_without_image=zh)

def del_zh_without_image(caption_obj, user_obj):
    # 若存在则删除
    zhs = ZhWithoutImage.objects.filter(caption_obj=caption_obj, user_that_annots_it=user_obj).order_by('zh_without_image_id')
    if len(zhs) != 1:
        print(1)
        id = zhs[1].zh_without_image_id
        ZhWithoutImage.objects.filter(zh_without_image_id=id).delete()