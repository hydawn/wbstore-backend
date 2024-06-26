from django.urls import path
from .views import CsrfTokenAPI, get_user_detail, post_signup, get_echo, \
        get_user_loggedin, post_login, post_logout, \
        get_search_merchandise, \
        get_get_merchandise, post_make_order, \
        get_get_order, post_customer_change_order, get_search_customer_order

from .merchant_views import post_insert_merchandise, \
        post_merchant_change_order, get_get_merchant_merchandise, \
        get_search_merchant_order

from .customer_views import get_get_shopping_cart, post_add_to_shopping_cart, \
        get_check_shopping_cart, post_change_shopping_cart

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
    path('add_to_shopping_cart', post_add_to_shopping_cart),
    path('get_shopping_cart', get_get_shopping_cart),
    path('get_merchandise', get_get_merchandise),
    path('make_order', post_make_order),
    path('get_order', get_get_order),
    path('customer_change_order', post_customer_change_order),
    path('merchant_change_order', post_merchant_change_order),
    path('search_customer_order', get_search_customer_order),
    path('search_merchant_order', get_search_merchant_order),
    path('get_merchant_merchandise', get_get_merchant_merchandise),
    path('check_shopping_cart', get_check_shopping_cart),
    path('change_shopping_cart', post_change_shopping_cart),
]
