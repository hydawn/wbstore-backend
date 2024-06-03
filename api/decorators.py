# the official decorator_from_middleware, decorator_from_middleware_with_args
# isn't working. don't know why

import json
from http import HTTPStatus

from django.http import JsonResponse

from .widgets import get_user_role
from .models import Merchandise, RunningOrder


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
                return JsonResponse({'status': 'error', 'error': f'Unauthorized, requring user role of {role}'}, status=HTTPStatus.UNAUTHORIZED)
            return func(request)
        return wrapper
    return decor


def has_json_payload():
    '''
    POST requests must have json payload
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


def has_query_params(params: list[str]):
    '''
    GET request must have certain query params
    '''
    def decor(func):
        def wrapper(request):
            for i in params:
                if request.GET.get(i) is None:
                    return JsonResponse({'status': 'error', 'error': f'failed to get params: {i}'}, status=HTTPStatus.BAD_REQUEST)
            return func(request)
        return wrapper
    return decor


def merchandise_exist(method: str):
    '''
    is this so called decorator-orianted programming?
    assume has_json_payload
    '''
    def decor(func):
        def wrapper(request):
            if method == 'get':
                merchandise_id = request.GET.get('merchandise_id')
            else:
                merchandise_id = request.json_payload['merchandise_id']
            merch_query_list = Merchandise.objects.filter(pk=merchandise_id)
            if len(merch_query_list) == 0:
                return JsonResponse(
                        {'status': 'error', 'error': 'no such merchandise'},
                        status=HTTPStatus.BAD_REQUEST)
            request.merchandise = merch_query_list[0]
            return func(request)
        return wrapper
    return decor


def runningorder_exist(method: str):
    '''
    is this so called decorator-orianted programming?
    assume has_json_payload
    '''
    def decor(func):
        def wrapper(request):
            if method == 'post':
                order_id = request.json_payload['runningorder_id']
            else:
                # method == 'get'
                order_id = request.GET.get('runningorder_id')
            try:
                request.runningorder = RunningOrder.objects.get(pk=order_id)
            except RunningOrder.DoesNotExist as err:
                return JsonResponse(
                        {'status': 'error', 'error': f'no such order: {err}'},
                        status=HTTPStatus.BAD_REQUEST)
            return func(request)
        return wrapper
    return decor


def user_is_order_creater(request) -> bool:
    return request.user.id == request.runningorder.user.id


def user_is_order_taker(request) -> bool:
    ''' user is the order's merchandise's owner '''
    return request.user.id == request.runningorder.merchandise.added_by_user.id


def user_can_view_runningorder():
    '''
    user is creater of order or creater of merchandise
    '''
    def decor(func):
        def wrapper(request):
            if user_is_order_creater(request) or user_is_order_taker(request):
                return func(request)
            return JsonResponse({'status': 'error', 'error': 'user not authorised to view this order'}, status=HTTPStatus.BAD_REQUEST)
        return wrapper
    return decor


def user_can_modify_runningorder():
    def decor(func):
        def wrapper(request):
            action = request.json_payload['action']
            role = get_user_role(request.user.username)
            not_allowed = JsonResponse({'status': 'error', 'error': f'action {action} not allowed by your role {role}'}, status=HTTPStatus.BAD_REQUEST)
            allowed = {
                    'merchant': ['take', 'accept cancel'],
                    'customer': ['pay', 'cancel', 'finish'],
                    }
            if action not in allowed[role]:
                return not_allowed
            if role == 'merchant' and not user_is_order_taker(request):
                return not_allowed
            if role == 'customer' and not user_is_order_creater(request):
                return not_allowed
            return func(request)
        return wrapper
    return decor


def get_with_pages():
    def decor(func):
        def wrapper(request):
            try:
                request.per_page = int(request.GET.get('per_page', 4))
                request.page_number = int(request.GET.get('page_number', 1))
            except ValueError:
                return JsonResponse({'error': 'per_page and page should be integer number'}, status=HTTPStatus.BAD_REQUEST)
            return func(request)
        return wrapper
    return decor
