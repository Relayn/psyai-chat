from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import CustomUserCreationForm


class HomePageView(TemplateView):
    """Отображает главную страницу."""

    template_name = "home.html"


class SignUpView(CreateView):
    """Обрабатывает регистрацию нового пользователя."""

    form_class = CustomUserCreationForm
    # После успешной регистрации перенаправляем на страницу входа.
    success_url = reverse_lazy("login")
    template_name = "users/signup.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        return response


@login_required
def profile_view(request):
    """Отображает страницу личного кабинета."""
    return render(request, "users/profile.html")
