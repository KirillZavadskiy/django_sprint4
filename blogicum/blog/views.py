from blog.models import Category, Comment, Post
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import CommentForm, PostForm, ProfileForm

COUNT_OF_POST = 10
User = get_user_model()


class PostListView(ListView):
    '''Главная страница со всеми постами.'''

    model = Post
    ordering = 'id'
    paginate_by = COUNT_OF_POST

    def get_queryset(self):
        return (
            self.model.objects.select_related('author')
            .filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            )
            .annotate(comment_count=Count('comment'))
            .order_by('-pub_date')
        )


class PostDetailView(DetailView):
    '''Страница определенного поста.'''

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        self.data = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if self.request.user == self.data.author:
            return Post.objects.filter(
                pk=self.kwargs['post_id']
            )
        return Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
            pk=self.kwargs['post_id']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comment.select_related('author')
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


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    '''Редактирование поста.'''

    form_class = PostForm
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])

    def test_func(self):
        return self.get_object().author == self.request.user


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    '''Удаление поста.'''

    form_class = PostForm
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm()
        return context

    def test_func(self):
        return self.get_object().author == self.request.user


class CategoryPostsListView(ListView):
    '''Страница с постами определенной категории.'''

    model = Post
    paginate_by = COUNT_OF_POST
    template_name = 'blog/category.html'

    def get_queryset(self):
        get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True,
        )
        return (
            self.model.objects.select_related('category')
            .filter(
                category__slug=self.kwargs['category_slug'],
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            )
            .order_by('-pub_date')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug']
        )
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    '''Создание комментария.'''

    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    '''Редактирование комментария.'''

    form_class = CommentForm
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])

    def test_func(self):
        return self.get_object().author == self.request.user


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    '''Удаление комментария.'''

    form_class = CommentForm
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])

    def test_func(self):
        return self.get_object().author == self.request.user


class ProfileListView(ListView):
    '''Страница профиля.'''

    model = Post
    paginate_by = COUNT_OF_POST
    template_name = 'blog/profile.html'

    def get_queryset(self):
        if self.request.user == get_object_or_404(
            User,
            username=self.kwargs['username']
        ):
            return (
                self.model.objects.select_related('author')
                .filter(
                    author__username=self.kwargs['username']
                )
                .order_by('-pub_date')
                .annotate(comment_count=Count('comment'))
            )
        return (
            self.model.objects.select_related('author')
            .filter(
                author__username=self.kwargs['username'],
                is_published=True
            )
            .order_by('-pub_date')
            .annotate(comment_count=Count('comment'))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
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
