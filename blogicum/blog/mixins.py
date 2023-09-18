from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Count
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

from .forms import CommentForm, PostForm
from .models import Comment, Post

COUNT_OF_POST = 10


class BaseFormMixin:
    '''Родительский Миксин.'''

    model = Post
    paginate_by = COUNT_OF_POST

    def get_queryset_comment(self):
        return (
            Post.objects.select_related('author', 'category', 'location')
            .annotate(comment_count=Count('comments'))
            .order_by('-pub_date')
        )

    def get_queryset(self):
        return (
            self.get_queryset_comment()
            .filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            )
        )


class PostMixin(UserPassesTestMixin):
    '''Миксин для классов Post.'''

    form_class = PostForm
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])

    def test_func(self):
        return self.get_object().author == self.request.user


class CommentMixin:
    '''Миксин для классов Comment.'''

    form_class = CommentForm
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])

    def test_func(self) -> True:
        return self.get_object().author == self.request.user
