from django.core.paginator import Paginator

from blogicum.constants import COUNT_POSTS


def get_paginator(request, posts):
    """View фнукция пагинатора."""
    paginator = Paginator(posts, COUNT_POSTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
