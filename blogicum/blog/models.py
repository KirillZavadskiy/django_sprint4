from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.html import mark_safe

User = get_user_model()
AMT_SIGN_TITLE = 30


class PubCreatModel(models.Model):
    '''Абстрактная модель.'''

    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True,
    )

    class Meta:
        abstract = True


class Category(PubCreatModel):
    '''Модель Категорий.'''

    title = models.CharField(max_length=256, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=('Идентификатор страницы для URL; '
                   'разрешены символы латиницы, цифры, дефис и подчёркивание.')
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:AMT_SIGN_TITLE]


class Location(PubCreatModel):
    '''Модель Локаций.'''

    name = models.CharField(
        'Название места',
        max_length=256,
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:AMT_SIGN_TITLE]


@admin.display(
    description='Фото'
)
class Post(PubCreatModel):
    '''Модель поста.'''

    title = models.CharField('Заголовок', max_length=256)
    text = models.TextField('Текст', max_length=1000)
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text=('Если установить дату и время в будущем '
                   '— можно делать отложенные публикации.')
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор публикации',
        on_delete=models.CASCADE,
        related_name='posts',
    )
    location = models.ForeignKey(
        Location,
        models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        models.SET_NULL,
        null=True,
        verbose_name='Категория',
        related_name='posts',
    )
    image = models.ImageField('Фото', upload_to='images', blank=True)

    def image_tag(self):
        return mark_safe(
            '<img src="/%s" width="150" height="150" />' % (self.image)
        )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title[:AMT_SIGN_TITLE]

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.pk})


class Comment(PubCreatModel):
    '''Модель комментария к посту.'''

    text = models.TextField("Текст комментария", max_length=256)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='comments'
    )
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ("created_at",)

    def __str__(self):
        return self.text[:AMT_SIGN_TITLE]
