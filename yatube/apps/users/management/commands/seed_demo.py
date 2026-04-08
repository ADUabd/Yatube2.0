import random
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.posts.models import Comment, Like, Post
from apps.users.models import Follow, Profile

User = get_user_model()


FIRST_NAMES = [
    'Anna', 'Max', 'Olga', 'Ivan', 'Sofia', 'Nikita', 'Maria', 'Artem',
    'Elena', 'Roman', 'Daria', 'Pavel', 'Alina', 'Denis', 'Kira', 'Timur',
    'Vera', 'Maksim', 'Polina', 'Egor',
]

LAST_NAMES = [
    'Smirnova', 'Ivanov', 'Petrova', 'Sokolov', 'Kuznetsova', 'Volkov',
    'Lebedeva', 'Morozov', 'Nikolaeva', 'Fedorov', 'Orlova', 'Pavlov',
]

LOCATIONS = [
    'Moscow', 'Saint Petersburg', 'Kazan', 'Sochi', 'Minsk', 'Tbilisi',
    'Yerevan', 'Belgrade', 'Almaty', 'Tashkent',
]

BIO_TEMPLATES = [
    'Product designer who shares interface sketches and daily notes.',
    'Backend engineer writing about work, coffee and side projects.',
    'HR lead tracking team culture, hiring and onboarding ideas.',
    'Marketing manager collecting launch stories and experiments.',
    'Photographer posting short stories from trips and city walks.',
    'Founder building a small product and documenting the process.',
]

POST_OPENERS = [
    'Today I want to share a small update',
    'A quick note from the last sprint',
    'One thing that worked well this week',
    'We tested a new idea and here is the result',
    'A short story from the team routine',
    'Here is what changed after the latest release',
]

POST_TOPICS = [
    'about onboarding', 'about product research', 'about hiring',
    'about design review', 'about customer interviews',
    'about documentation', 'about the mobile version',
    'about team rituals', 'about analytics', 'about content planning',
]

POST_ENDINGS = [
    'The feedback was much stronger than expected.',
    'This made the workflow easier for everyone involved.',
    'We will keep iterating on it next week.',
    'It is a small change, but the impact is visible already.',
    'This is the kind of progress worth showing in a demo.',
    'It helped align the team and reduced confusion.',
]

COMMENT_TEMPLATES = [
    'Looks solid. This is easy to understand.',
    'I like the direction here.',
    'This would be useful to show during a demo.',
    'The before/after difference is noticeable.',
    'Nice update. Keep posting these.',
    'This makes the product feel much more alive.',
]

DEMO_IMAGE_PATHS = [
    'posts/demo_card_01.svg',
    'posts/demo_card_02.svg',
    'posts/demo_card_03.svg',
]


class Command(BaseCommand):
    help = 'Заполняет базу демонстрационными пользователями, профилями, постами, комментариями, лайками и подписками.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=12,
            help='Количество демо-пользователей. По умолчанию: 12.',
        )
        parser.add_argument(
            '--posts-per-user',
            type=int,
            default=3,
            help='Количество постов на каждого демо-пользователя. По умолчанию: 3.',
        )
        parser.add_argument(
            '--reset-demo',
            action='store_true',
            help='Удалить существующие demo_* данные перед генерацией.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        users_count = max(1, options['users'])
        posts_per_user = max(1, options['posts_per_user'])
        rng = random.Random(42)

        if options['reset_demo']:
            self._reset_demo_data()

        demo_users = self._create_demo_users(users_count, rng)
        posts = self._create_posts(demo_users, posts_per_user, rng)
        comments_count = self._create_comments(demo_users, posts, rng)
        likes_count = self._create_likes(demo_users, posts, rng)
        follows_count = self._create_follows(demo_users, rng)

        self.stdout.write(self.style.SUCCESS('Demo data created successfully.'))
        self.stdout.write(f'Users: {len(demo_users)}')
        self.stdout.write(f'Posts: {len(posts)}')
        self.stdout.write(f'Comments: {comments_count}')
        self.stdout.write(f'Likes: {likes_count}')
        self.stdout.write(f'Follows: {follows_count}')
        self.stdout.write('Demo accounts password: demo12345')

    def _reset_demo_data(self):
        demo_users = User.objects.filter(username__startswith='demo_')
        deleted_users = demo_users.count()
        demo_users.delete()
        self.stdout.write(f'Removed existing demo users: {deleted_users}')

    def _create_demo_users(self, users_count, rng):
        demo_users = []

        for index in range(1, users_count + 1):
            username = f'demo_{index:02d}'
            email = f'{username}@example.com'
            first_name = FIRST_NAMES[(index - 1) % len(FIRST_NAMES)]
            last_name = LAST_NAMES[(index - 1) % len(LAST_NAMES)]

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                },
            )

            updated = False
            if user.email != email:
                user.email = email
                updated = True
            if user.first_name != first_name:
                user.first_name = first_name
                updated = True
            if user.last_name != last_name:
                user.last_name = last_name
                updated = True
            if created or not user.has_usable_password():
                user.set_password('demo12345')
                updated = True
            if updated:
                user.save()

            profile, _ = Profile.objects.get_or_create(user=user)
            profile.bio = BIO_TEMPLATES[(index - 1) % len(BIO_TEMPLATES)]
            profile.location = LOCATIONS[(index - 1) % len(LOCATIONS)]
            profile.website = f'https://example.com/{username}'
            profile.birth_date = timezone.localdate() - timedelta(days=8000 + index * 120)
            profile.save()

            demo_users.append(user)
            verb = 'Created' if created else 'Updated'
            self.stdout.write(f'{verb} user {username}')

        return demo_users

    def _create_posts(self, users, posts_per_user, rng):
        posts = []
        available_images = self._get_available_demo_images()

        for user_index, user in enumerate(users, start=1):
            for post_index in range(1, posts_per_user + 1):
                text = self._build_post_text(user_index, post_index)
                post, created = Post.objects.get_or_create(
                    author=user,
                    text=text,
                )

                if created:
                    created_at = timezone.now() - timedelta(
                        days=(user_index * 2) + post_index,
                        hours=rng.randint(0, 20),
                        minutes=rng.randint(0, 59),
                    )
                    Post.objects.filter(pk=post.pk).update(
                        created_at=created_at,
                        updated_at=created_at + timedelta(hours=rng.randint(0, 6)),
                    )
                    post.refresh_from_db()

                selected_image = None
                if available_images and (user_index + post_index) % 2 == 0:
                    selected_image = available_images[(user_index + post_index) % len(available_images)]

                image_name = post.image.name or None
                if selected_image and image_name != selected_image:
                    post.image.name = selected_image
                    post.save(update_fields=['image'])
                elif not selected_image and image_name:
                    post.image.delete(save=False)
                    post.image = None
                    post.save(update_fields=['image'])

                posts.append(post)

        return posts

    def _get_available_demo_images(self):
        available = []

        for relative_path in DEMO_IMAGE_PATHS:
            if Path(settings.MEDIA_ROOT, relative_path).exists():
                available.append(relative_path)

        return available

    def _create_comments(self, users, posts, rng):
        comments_created = 0

        for index, post in enumerate(posts):
            eligible_users = [user for user in users if user != post.author]
            sample_size = min(len(eligible_users), 2 + (index % 3))
            for comment_index, user in enumerate(rng.sample(eligible_users, sample_size), start=1):
                text = f'{COMMENT_TEMPLATES[(index + comment_index) % len(COMMENT_TEMPLATES)]} #{post.pk}'
                _, created = Comment.objects.get_or_create(
                    post=post,
                    author=user,
                    text=text,
                )
                if created:
                    comments_created += 1

        return comments_created

    def _create_likes(self, users, posts, rng):
        likes_created = 0

        for index, post in enumerate(posts):
            eligible_users = [user for user in users if user != post.author]
            sample_size = min(len(eligible_users), 3 + (index % 5))
            for user in rng.sample(eligible_users, sample_size):
                _, created = Like.objects.get_or_create(post=post, user=user)
                if created:
                    likes_created += 1

        return likes_created

    def _create_follows(self, users, rng):
        follows_created = 0

        for index, user in enumerate(users):
            other_users = [candidate for candidate in users if candidate != user]
            sample_size = min(len(other_users), 3 + (index % 4))
            for author in rng.sample(other_users, sample_size):
                _, created = Follow.objects.get_or_create(user=user, author=author)
                if created:
                    follows_created += 1

        return follows_created

    def _build_post_text(self, user_index, post_index):
        opener = POST_OPENERS[(user_index + post_index - 2) % len(POST_OPENERS)]
        topic = POST_TOPICS[(user_index * post_index - 1) % len(POST_TOPICS)]
        ending = POST_ENDINGS[(user_index + post_index - 2) % len(POST_ENDINGS)]
        return (
            f'{opener} {topic}. '
            f'Post #{post_index} from demo profile #{user_index}. '
            f'{ending}'
        )
