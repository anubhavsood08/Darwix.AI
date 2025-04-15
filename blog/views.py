from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import BlogPost


def blog_post_list(request):
    """View for listing all blog posts"""
    posts = BlogPost.objects.filter(published=True)
    return render(request, 'blog/post_list.html', {'posts': posts})


def blog_post_detail(request, post_id):
    """View for displaying a single blog post"""
    post = get_object_or_404(BlogPost, id=post_id, published=True)
    return render(request, 'blog/post_detail.html', {'post': post})


@login_required
def blog_post_create(request):
    """View for creating a new blog post"""
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        published = request.POST.get('published', False) == 'on'
        
        # Create new blog post
        post = BlogPost.objects.create(
            title=title,
            content=content,
            author=request.user,
            published=published
        )
        
        return redirect('blog:post_detail', post_id=post.id)
    
    return render(request, 'blog/post_form.html')


@login_required
def blog_post_edit(request, post_id):
    """View for editing an existing blog post"""
    post = get_object_or_404(BlogPost, id=post_id, author=request.user)
    
    if request.method == 'POST':
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.published = request.POST.get('published', False) == 'on'
        post.save()
        
        return redirect('blog:post_detail', post_id=post.id)
    
    return render(request, 'blog/post_form.html', {'post': post})