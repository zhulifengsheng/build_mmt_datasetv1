import os

def image_url(image_name):
    path_list = ['img', 'coco']
    path_list.extend(image_name.split('_'))
    return os.path.join(*path_list)