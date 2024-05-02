# the official decorator_from_middleware, decorator_from_middleware_with_args
# isn't working. don't know why

from http import HTTPStatus

from django.http import JsonResponse

from .widgets import get_user_role

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
