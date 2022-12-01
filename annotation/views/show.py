from django.shortcuts import render

from annotation.models import Image
from annotation.utils.backend import image_url

def show(request, image_id):
    res = {
        'image_id': image_id,
        'image_name': image_url(Image.objects.get(image_id=image_id).image_name),
    }
    return render(request, "show.html", res)