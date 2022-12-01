from django.shortcuts import render

from annotation.models import Caption, Image, RandomImageID, User

def first_page(request):
    '''
    首页
    '''
    # User.objects.create(username="lch", password="lv12345", is_admin=True)

    # import random
    # x = list(range(1, 123288))
    # random.shuffle(x)
    # for i in x:
    #     RandomImageID.objects.create(image_id=i)

    # dir = 'D:\\coco\\coco_caption\\images.txt'
    # with open(dir, 'r', encoding='utf-8') as f:
    #     for l in f:
    #         Image.objects.create(image_name=l.strip())

    # f1 = open('D:\\coco\\coco_caption\\captions.txt', 'r', encoding='utf-8')
    # f2 = open('D:\\coco\\coco_caption\\captions_translation.txt', 'r', encoding='utf-8')
    # idx, no = 1, 1
    # for l1, l2 in zip(f1, f2):
    #     l1, l2 = l1.strip(), l2.strip()
    #     if l1 == "":
    #         no = 1
    #         idx += 1
    #         continue
        
    #     Caption.objects.create(caption_NO=no, caption=l1, zh_machine_translation=l2, image_obj=Image.objects.filter(image_id=idx).first())
    #     no += 1

    is_admin = False
    if request.session.get("info") is not None and 'username' in request.session.get("info"):
        user_obj = User.objects.get(username=request.session.get("info")['username'])
        is_admin = user_obj.is_admin
    
    res = {
        'is_admin': is_admin,
    }
    return render(request, 'first_page.html', res)