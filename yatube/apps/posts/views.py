from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)

from .forms import PostForm, CommentForm
from .models import Post, Comment, Like

User = get_user_model()


class PostListMixin:
    """Миксин для списков постов."""
    
    def get_base_queryset(self):
        return Post.objects.select_related(
            'author',
            'author__profile'
        ).prefetch_related(
            'comments',
            'likes'
        ).annotate(
            likes_count=Count('likes', distinct=True),
            comments_count=Count('comments', distinct=True)
        )


class IndexView(PostListMixin, ListView):
    """Главная страница - все посты."""
    
    template_name = 'posts/index.html'
    context_object_name = 'posts'
    paginate_by = settings.POSTS_PER_PAGE

    def get_queryset(self):
        return self.get_base_queryset().order_by('-created_at')


class FeedView(LoginRequiredMixin, PostListMixin, ListView):
    """Лента подписок."""
    
    template_name = 'posts/feed.html'
    context_object_name = 'posts'
    paginate_by = settings.POSTS_PER_PAGE

    def get_queryset(self):
        following_ids = self.request.user.follower.values_list('author_id', flat=True)
        return self.get_base_queryset().filter(
            author_id__in=following_ids
        ).order_by('-created_at')


class PostDetailView(DetailView):
    """Детальная страница поста."""
    
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.select_related(
            'author',
            'author__profile'
        ).prefetch_related(
            'comments__author__profile',
            'likes'
        ).annotate(
            likes_count=Count('likes', distinct=True),
            comments_count=Count('comments', distinct=True)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        
        # Проверяем, лайкнул ли текущий пользователь пост
        if self.request.user.is_authenticated:
            context['is_liked'] = Like.objects.filter(
                post=self.object,
                user=self.request.user
            ).exists()
        else:
            context['is_liked'] = False
        
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание нового поста."""
    
    model = Post
    form_class = PostForm
    template_name = 'posts/post_create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Пост успешно создан!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('posts:post_detail', kwargs={'pk': self.object.pk})


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование поста."""
    
    model = Post
    form_class = PostForm
    template_name = 'posts/post_edit.html'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def form_valid(self, form):
        messages.success(self.request, 'Пост успешно обновлен!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('posts:post_detail', kwargs={'pk': self.object.pk})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление поста."""
    
    model = Post
    template_name = 'posts/post_confirm_delete.html'
    success_url = reverse_lazy('posts:index')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def form_valid(self, form):
        messages.success(self.request, 'Пост успешно удален!')
        return super().form_valid(form)


class LikeView(LoginRequiredMixin, View):
    """Лайк/анлайк поста."""
    
    def post(self, request, pk):
        try:
            post = get_object_or_404(Post, pk=pk)
        except Exception:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'error': 'Пост не найден.'
                }, status=404)
            messages.error(request, 'Пост не найден.')
            return redirect('posts:index')
        
        like, created = Like.objects.get_or_create(
            post=post,
            user=request.user
        )
        
        if not created:
            like.delete()
            liked = False
        else:
            liked = True
        
        # Для AJAX запросов
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'liked': liked,
                'likes_count': post.likes.count()
            })
        
        return redirect('posts:post_detail', pk=pk)


class CommentCreateView(LoginRequiredMixin, View):
    """Создание комментария."""
    
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        form = CommentForm(request.POST)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Комментарий добавлен!')
        else:
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{error}')
            else:
                messages.error(request, 'Ошибка при добавлении комментария.')
        
        return redirect('posts:post_detail', pk=pk)


class CommentDeleteView(LoginRequiredMixin, View):
    """Удаление комментария."""
    
    def post(self, request, pk, comment_pk):
        try:
            comment = get_object_or_404(
                Comment,
                pk=comment_pk,
                post_id=pk
            )
        except Exception:
            messages.error(request, 'Комментарий не найден.')
            return redirect('posts:index')
        
        if request.user == comment.author or request.user == comment.post.author:
            comment.delete()
            messages.success(request, 'Комментарий удален.')
        else:
            messages.error(request, 'У вас нет прав на удаление этого комментария.')
        
        return redirect('posts:post_detail', pk=pk)


class SearchView(PostListMixin, ListView):
    """Поиск постов."""
    
    template_name = 'posts/search.html'
    context_object_name = 'posts'
    paginate_by = settings.POSTS_PER_PAGE

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return self.get_base_queryset().filter(
                Q(text__icontains=query) |
                Q(author__username__icontains=query)
            ).order_by('-created_at')
        return Post.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context
