from django.urls import path
from .views import CsrfTokenAPI, LoginAPI, SignupAPI, get_user_detail, \
        get_echo, get_user_loggedin, post_logout, post_insert_merchandise, \
        get_search_merchandise, post_add_to_shopping_chart

urlpatterns = [
    path('login', LoginAPI.as_view()),
    path('logout', post_logout),
    path('signup', SignupAPI.as_view()),
    path('get_csrf_token', CsrfTokenAPI.as_view()),
    path('get_user_detail', get_user_detail),
    path('get_user_loggedin', get_user_loggedin),
    path('echo', get_echo),
    path('insert_merchandise', post_insert_merchandise),
    path('search_merchandise', get_search_merchandise),
    path('add_to_shopping_chart', post_add_to_shopping_chart),
]
