from django import forms
from django.contrib.auth import get_user_model

from .models import Comment, Post

User = get_user_model()


class PostForm(forms.ModelForm):
    '''Форма поста.'''

    class Meta:
        model = Post
        exclude = ('author', 'is_published')
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'datetime-local'})
        }


class CommentForm(forms.ModelForm):
    '''Форма комментария.'''

    class Meta:
        model = Comment
        fields = ('text',)


class ProfileForm(forms.ModelForm):
    '''Форма профиля.'''

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
