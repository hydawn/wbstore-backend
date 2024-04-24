from django.urls import path
from .views import CsrfTokenAPI, LoginAPI, SignupAPI, get_user_detail, get_echo, \
        get_user_loggedin

urlpatterns = [
    path('login', LoginAPI.as_view()),
    path('signup', SignupAPI.as_view()),
    path('get_csrf_token', CsrfTokenAPI.as_view()),
    path('get_user_detail', get_user_detail),
    path('get_user_loggedin', get_user_loggedin),
    path('echo', get_echo),
]
