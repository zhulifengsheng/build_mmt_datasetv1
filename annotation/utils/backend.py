import os
from annotation.models import User

def image_url(image_name):
    path_list = ['img', 'coco']
    path_list.extend(image_name.split('_'))
    return os.path.join(*path_list)

# 给用户添加任务
def util_management_add(username, task, user_obj):
    if task == 'first':
        # 给用户添加第一阶段的任务
        User.objects.filter(username=username).update(total_amount_without_image=user_obj.total_amount_without_image+num)
    else:
        # 给用户添加第二阶段的任务
        User.objects.filter(username=username).update(total_amount_with_image=user_obj.total_amount_with_image+num)    