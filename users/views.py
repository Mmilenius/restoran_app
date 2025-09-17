from .forms import ProfileForm
from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

# Залишаємо тільки logout view, оскільки login/signup будуть через AllAuth
@method_decorator(login_required, name='dispatch')
class UserLogoutView(View):
    def get(self, request):
        messages.success(request, f'{request.user.username}, Ви вийшли з аккаунта')
        auth.logout(request)
        return redirect(reverse('main:index'))

# View для підтвердження email
class EmailConfirmationSentView(TemplateView):
    template_name = 'account/verification_sent.html'

@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Ваш профіль оновлено!")
            return redirect("users:profile")
    else:
        form = ProfileForm(instance=request.user)

    context = {
        "form": form,
    }
    return render(request, "users/profile.html", context)