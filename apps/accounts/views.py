from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy

from .forms import NotifiLoginForm


class NotifiLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = NotifiLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('dashboard:index')


def logout_view(request):
    logout(request)
    return redirect('login')
