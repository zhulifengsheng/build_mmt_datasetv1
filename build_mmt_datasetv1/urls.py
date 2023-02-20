"""build_mmt_datasetv1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path
from annotation.views import show, api, first_page, management, annot

urlpatterns = [
    # 网址
    path('', first_page.first_page),
    path('show/<int:image_id>/', show.show),
    path('annotation_without_image/<int:index_without_image>/', annot.annotation_without_image),
    path('annotation_with_image/<int:index_with_image>/', annot.annotation_with_image),
    path('management/', management.management),
    # path('check_annotation/', ),

    # API
    path('api/login/', api.login),
    path('api/show_zh_table/', api.show_zh_table),
    path('api/show_en_table/', api.show_en_table),
    path('api/show_management_table/', api.show_management_table),
    path('api/management_add/', api.management_add),
    path('api/management_del/', api.management_del),

    # 获取当前用户的标注任务信息，并在后端进行重定向的跳转
    path('api/to_annotation_without_image/', api.to_annotation_without_image),
    path('api/get_annotation_without_image/', api.get_annotation_without_image),
    path('api/to_annotation_with_image/', api.to_annotation_with_image),
    path('api/get_annotation_with_image/', api.get_annotation_with_image),
]
