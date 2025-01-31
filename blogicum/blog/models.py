"""Файл моделей."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models

from blog.managers import PostManager
from blogicum.constants import CHARACTER_RESTRICTION, MAX_NAME_LENG


User = get_user_model()


class BaseModel(models.Model):
    """Базовая модель, от которой наследуются другие."""

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        """Абстрактная модель."""

        ordering = ['-created_at']
        abstract = True


class Category(BaseModel):
    """Модель категории."""

    title = models.CharField(max_length=MAX_NAME_LENG,
                             verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; '
                  'разрешены символы латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta(BaseModel.Meta):
        """Абстрактная модель."""

        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        """Магический метод дял админки."""
        return self.title[:CHARACTER_RESTRICTION]


class Location(BaseModel):
    """Модель для локации."""

    name = models.CharField(max_length=MAX_NAME_LENG,
                            verbose_name='Имя места')

    class Meta(BaseModel.Meta):
        """Абстрактная модель."""

        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'


class Post(BaseModel):
    """Модель для постов."""

    title = models.CharField(
        max_length=MAX_NAME_LENG,
        verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        blank=False,
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем — '
                  'можно делать отложенные публикации.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='posts'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение',
        related_name='posts'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
        related_name='posts'
    )
    image = models.ImageField(
        'Фото',
        upload_to='blogicum_images',
        blank=True
    )

    objects = models.Manager()
    published_posts = PostManager()

    class Meta(BaseModel.Meta):
        """Абстрактная модель."""

        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        """Магический метод дял админки."""
        return self.title[:CHARACTER_RESTRICTION]


class Comment(models.Model):
    text = models.TextField('Написать комментарий')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Публикация',
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='comments'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавленно'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)

    def __str__(self):
        """Магический метод дял админки."""
        return self.title[:CHARACTER_RESTRICTION]
