from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('posts/', views.blog_post_list, name='post_list'),
    path('posts/<int:post_id>/', views.blog_post_detail, name='post_detail'),
    path('posts/create/', views.blog_post_create, name='post_create'),
    path('posts/<int:post_id>/edit/', views.blog_post_edit, name='post_edit'),
]