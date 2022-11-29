from django.shortcuts import render

def first_page(request):
    # 首页
    return render(request, 'first_page.html')