"""Файл для констант."""
from django.core.paginator import Paginator

MAX_NAME_LENG = 256
CHARACTER_RESTRICTION = 10
COUNT_POSTS = 10


def get_paginator(request, posts):
    """View фнукция пагинатора."""
    paginator = Paginator(posts, COUNT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'page_obj': page_obj,
    }
