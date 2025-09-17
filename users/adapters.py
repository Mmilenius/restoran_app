from django.contrib import messages
from django.urls import reverse
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):

    def get_login_redirect_url(self, request):
        """Редирект після логіну"""
        return reverse('main:index')

    def get_logout_redirect_url(self, request):
        """Редирект після логауту"""
        return reverse('main:index')

    def add_message(self, request, level, message_tag, message, extra_tags='', fail_silently=False):
        """Додаємо кастомні повідомлення"""
        if message_tag == 'account_logged_in':
            messages.success(request, f'{request.user.username}, Ви ввійшли в аккаунт')
        elif message_tag == 'account_logged_out':
            messages.success(request, 'Ви вийшли з аккаунта')
        elif message_tag == 'account_verified':
            messages.success(request, 'Email успішно підтверджено!')
        else:
            super().add_message(request, level, message_tag, message, extra_tags, fail_silently)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def get_connect_redirect_url(self, request, socialaccount):
        """Редирект після підключення соцмережі"""
        return reverse('main:index')

    def populate_user(self, request, sociallogin, data):
        """Автоматично заповнюємо поля користувача з Google"""
        user = super().populate_user(request, sociallogin, data)

        # Заповнюємо ім'я та прізвище з Google
        if sociallogin.account.provider == 'google':
            extra_data = sociallogin.account.extra_data
            user.first_name = extra_data.get('given_name', '')
            user.last_name = extra_data.get('family_name', '')

        return user