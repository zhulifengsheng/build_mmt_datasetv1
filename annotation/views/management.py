from django.shortcuts import render
from django.http import Http404

from annotation.models import User

def management(request):
    user_obj = User.objects.filter(username=request.session.get("info")['username']).first()
    if user_obj.is_admin:
        # 只有管理员用户才能看见该网页
        return render(request, 'management.html')
    
    return Http404("非法访问")