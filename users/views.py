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
        # Примечание: Стандартный CreateView сам сохраняет пользователя.
        # Этот метод можно было бы и не переопределять, но для ясности
        # можно оставить, чтобы видеть, что происходит.
        response = super().form_valid(form)
        # Можно автоматически залогинить пользователя после регистрации,
        # но для MVP лучше явный шаг входа.
        # login(self.request, self.object)
        return response


@login_required
def profile_view(request):
    """Отображает страницу личного кабинета."""
    return render(request, "users/profile.html")
