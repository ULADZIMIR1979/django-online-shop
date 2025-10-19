from django.contrib.auth.views import LoginView
from django.urls import path

from .views import (
    get_cookie_view,
    set_cookie_view,
    set_session_view,
    get_session_view,
    MyLogoutView,
    AboutMeView,
    RegisterView,
    FooBarView,
    UserListView,
    UserDetailView,
    ProfileUpdateView,
)

app_name = 'myauth'

urlpatterns = [
    path(
        'login/',
        LoginView.as_view(
            template_name='myauth/login.html',
            redirect_authenticated_user=True,
        ),
        name='login'
    ),
    path("logout/", MyLogoutView.as_view(), name='logout'),
    path("about-me/", AboutMeView.as_view(), name='about-me'),
    path("register/", RegisterView.as_view(), name='register'),

    # Новые URL для пользователей
    path("users/", UserListView.as_view(), name='users-list'),
    path("users/<int:user_id>/", UserDetailView.as_view(), name='user-detail'),
    path("users/<int:user_id>/update/", ProfileUpdateView.as_view(), name='profile-update'),

    path("cookie/get/", get_cookie_view, name='cookie_get'),
    path("cookie/set/", set_cookie_view, name='cookie_set'),

    path("session/set/", set_session_view, name='session_set'),
    path("session/get/", get_session_view, name='session_get'),

    path("foo-bar/", FooBarView.as_view(), name='foo-bar'),
]