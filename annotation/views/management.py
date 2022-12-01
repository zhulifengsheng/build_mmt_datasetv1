from django.shortcuts import render
from django.http import Http404

from annotation.models import User

def management(request):
    if request.session.get("info") is None or 'username' not in request.session.get("info"):
        raise Http404("非法访问")
    
    user_obj = User.objects.get(username=request.session.get("info")['username'])
    if user_obj.is_admin:
        # 只有管理员用户才能看见该网页
        user_objs = User.objects.all()
        res = {
            'usernames': [i.username for i in user_objs],
        }

        return render(request, 'management.html', res)
    
    raise Http404("非法访问")