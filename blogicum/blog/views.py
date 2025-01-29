"""Views функции blogicum."""
import datetime as dt

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from blog.constants import get_paginator
from blog.forms import CommentForm, PostForm, UserForm
from blog.models import Category, Comment, Post

User = get_user_model()


def index(
        request
):
    """View функция главной страницы blogicum."""
    post_list = Post.published_posts.select_related(
        'author',
        'location',
        'category'
    ).order_by(
        '-pub_date'
    ).annotate(
        comment_count=Count(
            'comments'
        )
    )
    context = {
        'post_list': post_list
    }
    context.update(
        get_paginator(
            request,
            post_list
        )
    )
    return render(
        request,
        'blog/index.html',
        context
    )


def post_detail(
        request,
        post_id
):
    """View функция подробной страницы."""
    post = get_object_or_404(
        Post.objects.select_related(
            'category',
            'location',
            'author'
        ), id=post_id
    )
    if post.author != request.user:
        post = get_object_or_404(
            Post.objects.select_related(
                'category',
                'location',
                'author'
            ).filter(
                pub_date__lt=dt.datetime.now(),
                category__is_published=True,
                is_published=True,
                id=post_id
            )
        )
    return render(
        request,
        'blog/detail.html',
        {
            'post': post,
            'form': CommentForm(),
            'comments': Comment.objects.all().filter(
                post_id=post_id
            )
        }
    )


def category_posts(request,
                   category_slug
                   ):
    """View функция категорий."""
    category = get_object_or_404(
        Category.objects.filter(
            slug=category_slug
        ), is_published=True,
    )
    posts = category.posts(
        manager='published_posts'
    ).all()
    context = {
        'category': category
    }
    context.update(
        get_paginator(
            request,
            posts
        )
    )
    return render(
        request,
        'blog/category.html',
        context
    )


@login_required
def create_post(
    request
):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        instance = form.save(
            commit=False
        )
        instance.author = request.user
        instance.save()
        return redirect(
            'blog:profile',
            username=request.user
        )
    return render(
        request,
        'blog/create.html',
        {
            'form': form
        }
    )


def profile(
        request,
        username
):
    profile = get_object_or_404(
        User,
        username=username
    )
    posts = Post.objects.filter(
        author=profile
    ).order_by(
        '-pub_date'
    ).annotate(
        comment_count=Count('comments')
    )
    context = {
        'profile': profile
    }
    context.update(
        get_paginator(
            request,
            posts
        )
    )
    return render(
        request,
        'blog/profile.html',
        context,
    )


@login_required
def edit_profile(
        request
):
    instance = get_object_or_404(
        User,
        username=request.user
    )
    form = UserForm(
        request.POST,
        instance=instance
    )
    if form.is_valid():
        form.save()
    return render(
        request,
        'blog/user.html',
        {
            'form': form
        }
    )


@login_required
def edit_post(
    request,
    post_id
):
    post = get_object_or_404(
        Post,
        id=post_id
    )
    if request.user != post.author:
        return redirect(
            'blog:post_detail',
            post_id
        )
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect(
            'blog:post_detail',
            post_id
        )
    return render(
        request,
        'blog/create.html',
        {
            'form': form,
            'post': post,
            'is_edit': True
        }
    )


@login_required
def edit_comment(
        request,
        post_id,
        comment_id
):
    comment = get_object_or_404(
        Comment,
        id=comment_id
    )
    user = Comment.objects.get(
        pk=comment_id
    )
    if request.user != user.author:
        return redirect(
            'blog:post_detail',
            post_id
        )
    form = CommentForm(
        request.POST or None,
        files=request.FILES or None,
        instance=comment
    )
    if form.is_valid():
        form.save()
        return redirect(
            'blog:post_detail',
            post_id
        )
    return render(
        request,
        'blog/comment.html',
        {
            'form': form,
            'comment': comment,
            'is_edit': True
        }
    )


@login_required
def delete_post(
    request,
    post_id
):
    post = get_object_or_404(
        Post,
        id=post_id
    )
    instance = get_object_or_404(
        Post,
        id=post_id
    )
    form = PostForm(
        instance=instance
    )
    if request.user != post.author:
        return redirect(
            'blog:post_detail',
            post_id
        )
    if request.method == 'POST':
        instance.delete()
        return redirect(
            'blog:index'
        )
    return render(
        request,
        'blog/create.html',
        {
            'form': form
        }
    )


@login_required
def delete_comment(
    request,
    comment_id,
    post_id
):
    instance = get_object_or_404(
        Comment,
        id=comment_id
    )
    if request.user != instance.author:
        return redirect(
            'blog:post_detail',
            post_id
        )
    if request.method == 'POST':
        instance.delete()
        return redirect(
            'blog:post_detail',
            post_id
        )
    return render(
        request,
        'blog/comment.html'
    )


@login_required
def add_comment(
    request,
    post_id,
    comment_id=None
):
    post = get_object_or_404(
        Post,
        id=post_id
    )
    if request.method == 'POST':
        if comment_id:
            form = CommentForm(
                instance=Comment.objects.get(
                    id=comment_id
                ), data=request.POST
            )
        else:
            form = CommentForm(
                data=request.POST
            )
        if form.is_valid():
            comment = form.save(
                commit=False
            )
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect(
                'blog:post_detail',
                post_id=post_id
            )
        else:
            return render(
                request,
                'comments.html',
                {
                    'form': form,
                    'post': post
                }
            )
    else:
        form = CommentForm()
    return render(
        request,
        'comments.html',
        {
            'form': form,
            'post': post
        }
    )
