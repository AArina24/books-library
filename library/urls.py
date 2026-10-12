from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_file, name='upload'),
    path('files/', views.files_list, name='files'),
    path('files/<str:filename>/', views.file_detail, name='file_detail'),
]