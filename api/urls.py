from django.urls import path
from django.contrib.auth.views import LoginView
from .views import CsrfTokenAPI, LoginAPI, SignupAPI, UserDetailAPI

urlpatterns = [
    path('login/', LoginAPI.as_view()),
    path('signup/', SignupAPI.as_view()),
    path('get_csrf_token/', CsrfTokenAPI.as_view()),
    path('userdetail/', UserDetailAPI.as_view()),
]
