from django import forms
from django.contrib.auth import get_user_model

from blog.models import Comment, Post


User = get_user_model()


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name'
        )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = (
            'text',
        )


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = (
            'author',
        )
