from django.urls import path
from .views import CsrfTokenAPI, get_user_detail, post_signup, get_echo, \
        get_user_loggedin, post_login, post_logout, \
        get_search_merchandise, post_add_to_shopping_chart, \
        get_my_shopping_chart, post_make_order

from .merchant_views import post_insert_merchandise

urlpatterns = [
    path('login', post_login),
    path('logout', post_logout),
    path('signup', post_signup),
    path('get_csrf_token', CsrfTokenAPI.as_view()),
    path('get_user_detail', get_user_detail),
    path('get_user_loggedin', get_user_loggedin),
    path('echo', get_echo),
    path('insert_merchandise', post_insert_merchandise),
    path('search_merchandise', get_search_merchandise),
    path('add_to_shopping_chart', post_add_to_shopping_chart),
    path('my_shopping_chart', get_my_shopping_chart),
    path('make_order', post_make_order),
]
