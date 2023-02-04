import os
from annotation.models import User, RandomImageID, _MAX, Caption, Image, FirstStageWorkPool

def image_url(image_name):
    path_list = ['img', 'coco']
    path_list.extend(image_name.split('_'))
    return os.path.join(*path_list)

# 给用户添加任务
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
        # 给用户添加第二阶段的任务
        User.objects.filter(username=username).update(total_amount_with_image=user_obj.total_amount_with_image+num)    