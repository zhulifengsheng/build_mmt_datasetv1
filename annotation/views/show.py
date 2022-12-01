from django.shortcuts import render

from annotation.models import Image, User
from annotation.utils.backend import image_url

def show(request, image_id):
    is_admin = False
    if request.session.get("info") is not None and 'username' in request.session.get("info"):
        user_obj = User.objects.get(username=request.session.get("info")['username'])
        is_admin = user_obj.is_admin
    
    res = {
        'image_id': image_id,
        'image_name': image_url(Image.objects.get(image_id=image_id).image_name),
        'is_admin': is_admin,
    }
    return render(request, "show.html", res)