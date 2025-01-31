"""Views функции blogicum."""

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from blog.forms import CommentForm, PostForm, UserForm
from blog.models import Category, Comment, Post
from blogicum.utils import get_paginator


User = get_user_model()


def index(request):
    """View функция главной страницы blogicum."""
    return render(
        request,
        'blog/index.html',
        {
            'post_list': Post.published_posts.select_related(
                'author',
                'location',
                'category'
            ).order_by(
                '-pub_date'
            ).annotate(
                comment_count=Count(
                    'comments'
                )
            ),
            'page_obj': get_paginator(
                request,
                Post.published_posts.select_related(
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
            )
        }
    )


def post_detail(request, post_id):
    """View функция подробной страницы."""
    post = get_object_or_404(
        Post.objects.select_related(
            'category',
            'location',
            'author'
        ), id=post_id
    )
    if post.author != request.user and not (post.pub_date <= timezone.now()
                                            and post.category.is_published
                                            and post.is_published):
        raise Http404('Пост не найден/доступен')
    return render(
        request,
        'blog/detail.html',
        {
            'post': post,
            'form': CommentForm(),
            'comments': post.comments.filter(post_id=post_id)
        }
    )


def category_posts(request, category_slug):
    """View функция категорий."""
    return render(
        request,
        'blog/category.html',
        {
            'category': get_object_or_404(
                Category.objects.filter(
                    slug=category_slug
                ),
                is_published=True,
            ),
            'page_obj': get_paginator(
                request,
                get_object_or_404(
                    Category.objects.filter(
                        slug=category_slug
                    ),
                    is_published=True
                ).posts(
                    manager='published_posts'
                ).all()
            )
        }
    )


@login_required
def create_post(request):
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


def profile(request, username):
    profile = get_object_or_404(
        User,
        username=username
    )
    posts = Post.objects.select_related(
        'category',
        'location',
        'author'
    ).filter(author=profile).annotate(
        comment_count=Count(
            'comments'
        )
    ).order_by(
        '-pub_date'
    )
    if profile.id != request.user.id:
        posts = posts.filter(
            pub_date__lte=timezone.now(),
            category__is_published=True,
            is_published=True
        )
    return render(
        request,
        'blog/profile.html',
        {
            'profile': profile,
            'page_obj': get_paginator(
                request,
                posts
            )
        }
    )


@login_required
def edit_profile(request):
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
def edit_post(request, post_id):
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
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(
        Comment,
        id=comment_id
    )
    if request.user != Comment.objects.get(pk=comment_id).author:
        return redirect(
            'blog:post_detail',
            post_id
        )
    form = CommentForm(
        request.POST or None,
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
def delete_post(request, post_id):
    if request.user != get_object_or_404(Post, id=post_id).author:
        return redirect(
            'blog:post_detail',
            post_id
        )
    if request.method == 'POST':
        get_object_or_404(Post, id=post_id).delete()
        return redirect(
            'blog:index'
        )
    return render(
        request,
        'blog/create.html',
        {
            'form': PostForm(instance=get_object_or_404(Post, id=post_id))
        }
    )


@login_required
def delete_comment(request, comment_id, post_id):
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
def add_comment(request, post_id, comment_id=None):
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
        form = CommentForm()
    return render(
        request,
        'comments.html',
        {
            'form': form,
            'post': post
        }
    )
