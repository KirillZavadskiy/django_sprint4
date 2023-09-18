from django import forms

from .models import Comment, Post, User


class PostForm(forms.ModelForm):
    '''Форма поста.'''

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%d %H:%M:%S',
                attrs={'type': 'datetime-local'}
            )
        }


class CommentForm(forms.ModelForm):
    '''Форма комментария.'''

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {'text': forms.Textarea(attrs={'rows': '3'})}


class ProfileForm(forms.ModelForm):
    '''Форма профиля.'''

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
