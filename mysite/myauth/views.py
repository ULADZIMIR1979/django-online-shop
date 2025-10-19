from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView

from .models import Profile


class AboutMeView(UpdateView):
    model = Profile
    template_name = "myauth/about-me.html"
    fields = ['bio', 'avatar']
    success_url = reverse_lazy('myauth:about-me')

    def get_object(self, queryset=None):
        # Получаем или создаем профиль для текущего пользователя
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "myauth/register.html"
    success_url = reverse_lazy('myauth:about-me')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Создаем профиль для нового пользователя
        Profile.objects.create(user=self.object)

        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(
            self.request,
            username=username,
            password=password,
        )
        login(request=self.request, user=user)
        return response


# Добавляем новые view для списка пользователей и деталей профиля
class UserListView(ListView):
    template_name = "myauth/users-list.html"
    context_object_name = "profiles"

    def get_queryset(self):
        # Создаем профили для всех пользователей, у которых их нет
        users_without_profile = User.objects.filter(profile__isnull=True)
        for user in users_without_profile:
            Profile.objects.get_or_create(user=user)
        return Profile.objects.select_related('user').all()


class UserDetailView(DetailView):
    template_name = "myauth/user-detail.html"
    context_object_name = "profile"
    model = Profile

    def get_object(self, queryset=None):
        # Получаем профиль по user_id из URL, или создаем если нет
        user_id = self.kwargs.get('user_id')
        profile, created = Profile.objects.get_or_create(user_id=user_id)
        return profile


class ProfileUpdateView(UpdateView):
    model = Profile
    template_name = "myauth/profile-update.html"
    fields = ['bio', 'avatar']

    def get_success_url(self):
        return reverse_lazy('myauth:user-detail', kwargs={'user_id': self.object.user_id})

    def get_object(self, queryset=None):
        user_id = self.kwargs.get('user_id')
        profile, created = Profile.objects.get_or_create(user_id=user_id)
        return profile

    def dispatch(self, request, *args, **kwargs):
        # Проверка прав доступа
        profile = self.get_object()
        if not request.user.is_staff and request.user != profile.user:
            return HttpResponse("Forbidden", status=403)
        return super().dispatch(request, *args, **kwargs)


# Старые функции оставляем для обратной совместимости
def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/admin/')

        return render(request, 'myauth/login.html')

    username = request.POST['username']
    password = request.POST['password']

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('/admin/')

    return render(request, 'myauth/login.html', {"error": "Invalid credentials"})


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect(reverse('myauth:login'))


class MyLogoutView(LogoutView):
    next_page = reverse_lazy('myauth:login')


def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse('Cookie set')
    response.set_cookie('fizz', 'buzz', max_age=3600)
    return response


def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get('fizz', 'default value')
    return HttpResponse(f"Cookie value: {value!r}")


@permission_required('myauth.view_profile', raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session set!")


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default")
    return HttpResponse(f"Session value: {value!r}")


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam": "eggs"})