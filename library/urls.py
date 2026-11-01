from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_file, name='upload'),
    path('files/', views.files_list, name='files'),
    path('files/<str:filename>/', views.file_detail, name='file_detail'),
    path('files/<str:filename>/delete/', views.delete_file_view, name='delete_file'),
    path('db/', views.db_list, name='db_list'),
    path('db/search/', views.db_search_ajax, name='db_search_ajax'),
    path('db/edit/<int:book_id>/', views.edit_book, name='edit_book'),
    path('db/delete/<int:book_id>/', views.delete_book_db, name='delete_book_db'),
]