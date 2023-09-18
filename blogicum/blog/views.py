from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import CommentForm, PostForm, ProfileForm
from .mixins import BaseFormMixin, CommentMixin, PostMixin
from .models import Category, Post, User


class PostListView(BaseFormMixin, ListView):
    '''Главная страница со всеми постами.'''

    pass


class PostDetailView(LoginRequiredMixin, DetailView):
    '''Страница определенного поста.'''

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        data = (
            Post.objects.select_related('author', 'category', 'location')
            .filter(
                Q(author=self.request.user)
                | Q(
                    is_published=True,
                    category__is_published=True,
                    pub_date__lte=timezone.now()
                )
            )
        )
        return get_object_or_404(
            data,
            pk=self.kwargs.get('post_id'),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    '''Создание поста.'''

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile', args=[self.request.user.username]
        )


class PostUpdateView(
    LoginRequiredMixin, PostMixin, UpdateView
):
    '''Редактирование поста.'''

    pass


class PostDeleteView(
    LoginRequiredMixin, PostMixin, DeleteView
):
    '''Удаление поста.'''

    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = {'instance': self.object}
        return context


class CategoryPostsListView(BaseFormMixin, ListView):
    '''Страница с постами определенной категории.'''

    template_name = 'blog/category.html'

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True,
        )
        return (
            super().get_queryset().filter(
                category__slug=self.kwargs['category_slug']
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class CommentCreateView(LoginRequiredMixin, CommentMixin, CreateView):
    '''Создание комментария.'''

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentUpdateView(
    LoginRequiredMixin, CommentMixin, UserPassesTestMixin, UpdateView
):
    '''Редактирование комментария.'''

    pass


class CommentDeleteView(
    LoginRequiredMixin, CommentMixin, UserPassesTestMixin, DeleteView
):
    '''Удаление комментария.'''

    pass


class ProfileListView(BaseFormMixin, ListView):
    '''Страница профиля.'''

    template_name = 'blog/profile.html'

    def get_queryset(self):
        self.get_username = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        if self.request.user == self.get_username:
            return (
                self.get_queryset_comment()
                .filter(author__username=self.kwargs['username'])
            )
        return (
            super().get_queryset()
            .filter(author__username=self.kwargs['username'])
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_username
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    '''Редактирование профиля.'''

    form_class = ProfileForm
    model = User
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:index')
