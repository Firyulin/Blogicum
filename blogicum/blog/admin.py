"""Импорт модуля admin."""

from django.contrib import admin

from .models import Category, Location, Post, Comment


class PostAdmin(admin.ModelAdmin):
    title = ['title', 'pub_date', 'text', 'location', 'author', 'category']
    list_filter = ['pub_date']
    list_display = ['title', 'author', 'location']
    editable_list = ['category']


class CategoryAdmin(admin.ModelAdmin):
    title = ['title', 'slug', 'description']
    list_display = ['title', 'slug', 'description']
    list_filter = ['title']
    editable_list = ['slug']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Location)
admin.site.register(Comment)
