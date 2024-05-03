# the official decorator_from_middleware, decorator_from_middleware_with_args
# isn't working. don't know why

import json
from http import HTTPStatus

from django.http import JsonResponse

from .widgets import get_user_role
from .models import Merchandise

def allow_methods(allowed_methods: list[str]):
    '''
    the decorated function must be called with certain http methods
    '''
    def decor(func):
        def wrapper(request):
            print(type(request))
            if request.method not in allowed_methods:
                return JsonResponse({'error': 'Method Not Allowed'}, status=HTTPStatus.METHOD_NOT_ALLOWED)
            return func(request)
        return wrapper
    return decor


def login_required():
    '''
    decorated function must be called after user is authenticated
    '''
    def decor(func):
        def wrapper(request):
            if not request.user.is_authenticated:
                # or not request.user.is_permitted:
                return JsonResponse({'error': 'Unauthorized action, login required'}, status=HTTPStatus.UNAUTHORIZED)
            return func(request)
        return wrapper
    return decor


def role_required(role: str):
    '''
    the user must be of a certain role
    login_required
    '''
    def decor(func):
        def wrapper(request):
            if role != get_user_role(request.user.username):
                return JsonResponse({'status': 'error', 'error': 'requring user role of role'}, status=HTTPStatus.UNAUTHORIZED)
            return func(request)
        return wrapper
    return decor


def has_json_payload():
    '''
    requests must have json payload
    '''
    def decor(func):
        def wrapper(request):
            if request.content_type != 'application/json':
                return JsonResponse({'status': 'error', 'error': 'content_type must be application/json'}, status=HTTPStatus.BAD_REQUEST)
            try:
                # but how do I pass this form into func?
                # oh my, python is so flexible
                request.json_payload = json.loads(request.body)
            except json.JSONDecodeError as err:
                return JsonResponse({'status': 'error', 'error': f"payload can't be properly decoded: {err}"}, status=HTTPStatus.BAD_REQUEST)
            return func(request)
        return wrapper
    return decor


def merchandise_exist():
    '''
    is this so called decorator-orianted programming?
    assume has_json_payload
    '''
    def decor(func):
        def wrapper(request):
            merch_id = request.json_payload['merchandise_id']
            merch_query_list = Merchandise.objects.filter(pk=merch_id)
            if len(merch_query_list) == 0:
                return JsonResponse(
                        {'status': 'error', 'error': 'no such merchandise'},
                        status=HTTPStatus.BAD_REQUEST)
            request.merchandise = merch_query_list[0]
            return func(request)
        return wrapper
    return decor
