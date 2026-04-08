from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView, ListView

from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    ProfileUpdateForm,
    UserUpdateForm
)
from .models import Follow

User = get_user_model()


class SignUpView(CreateView):
    """Регистрация нового пользователя."""

    form_class = CustomUserCreationForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Регистрация прошла успешно! Войдите в систему.')
        return response


class CustomLoginView(LoginView):
    """Авторизация пользователя."""

    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'

    def form_valid(self, form):
        messages.success(self.request, f'Добро пожаловать, {form.get_user().username}!')
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    """Выход пользователя."""
    
    next_page = reverse_lazy('posts:index')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'Вы вышли из системы.')
        return super().dispatch(request, *args, **kwargs)


class ProfileDetailView(DetailView):
    """Просмотр профиля пользователя."""

    model = User
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_queryset(self):
        return User.objects.prefetch_related(
            'posts__likes',
            'posts__comments'
        ).annotate(
            followers_count=Count('following', distinct=True),
            following_count=Count('follower', distinct=True),
            posts_count=Count('posts', distinct=True)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = self.object

        # Проверяем подписку
        if self.request.user.is_authenticated:
            context['is_following'] = Follow.objects.filter(
                user=self.request.user,
                author=profile_user
            ).exists()
        else:
            context['is_following'] = False

        # Посты пользователя
        context['posts'] = profile_user.posts.select_related(
            'author'
        ).prefetch_related('likes', 'comments')[:10]

        return context


class ProfileUpdateView(LoginRequiredMixin, View):
    """Редактирование профиля."""

    template_name = 'users/profile_edit.html'

    def get_profile(self, user):
        """Получить или создать профиль пользователя."""
        from .models import Profile
        profile, _ = Profile.objects.get_or_create(user=user)
        return profile

    def get(self, request):
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=self.get_profile(request.user))
        return self.render_forms(request, user_form, profile_form)

    def post(self, request):
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=self.get_profile(request.user)
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('users:profile', username=request.user.username)

        return self.render_forms(request, user_form, profile_form)

    def render_forms(self, request, user_form, profile_form):
        from django.shortcuts import render
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form
        })


class FollowView(LoginRequiredMixin, View):
    """Подписка на пользователя."""

    def post(self, request, username):
        try:
            author = get_object_or_404(User, username=username)
        except Exception:
            messages.error(request, f'Пользователь {username} не найден.')
            return redirect('posts:index')

        if request.user == author:
            messages.error(request, 'Нельзя подписаться на себя.')
            return redirect('users:profile', username=username)

        follow, created = Follow.objects.get_or_create(
            user=request.user,
            author=author
        )

        if created:
            messages.success(request, f'Вы подписались на {author.username}.')
        else:
            messages.info(request, f'Вы уже подписаны на {author.username}.')

        return redirect('users:profile', username=username)


class UnfollowView(LoginRequiredMixin, View):
    """Отписка от пользователя."""

    def post(self, request, username):
        try:
            author = get_object_or_404(User, username=username)
        except Exception:
            messages.error(request, f'Пользователь {username} не найден.')
            return redirect('posts:index')

        deleted, _ = Follow.objects.filter(
            user=request.user,
            author=author
        ).delete()

        if deleted:
            messages.success(request, f'Вы отписались от {author.username}.')
        else:
            messages.info(request, f'Вы не были подписаны на {author.username}.')

        return redirect('users:profile', username=username)


class FollowersListView(ListView):
    """Список подписчиков."""

    template_name = 'users/followers.html'
    context_object_name = 'followers'
    paginate_by = 20

    def get_queryset(self):
        self.profile_user = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        return Follow.objects.filter(
            author=self.profile_user
        ).select_related(
            'user'
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user'] = self.profile_user
        return context


class FollowingListView(ListView):
    """Список подписок."""

    template_name = 'users/following.html'
    context_object_name = 'following'
    paginate_by = 20

    def get_queryset(self):
        self.profile_user = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        return Follow.objects.filter(
            user=self.profile_user
        ).select_related(
            'author'
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user'] = self.profile_user
        return context
