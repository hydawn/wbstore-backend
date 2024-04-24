#from django.shortcuts import render

import json
from http import HTTPStatus

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.csrf import get_token

from .decorators import login_required, allow_methods

from wbstorebackend.settings import DEBUG


class CsrfTokenAPI(View):
    def get(self, request):
        return JsonResponse({'csrfToken': get_token(request)})


class LoginAPI(View):
    def post(self, request: WSGIRequest):
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username and request.content_type == 'application/json':
            # this is API version of post where data is in payload
            # quite strange
            username = json.loads(request.body).get('username')
            password = json.loads(request.body).get('password')
        if DEBUG:
            print(f'got user [{username}] try to login')
        if request.user.is_authenticated:
            return JsonResponse({'status': f'[{username}] already logged in'}, status=HTTPStatus.OK)
        if not (username and password):
            return JsonResponse({'error': f'Username [{username}] or Password [{password}] not provided or Empty'}, status=HTTPStatus.BAD_REQUEST)
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            ok_message = {'status': 'ok', 'action': 'login', 'username': username}
            return JsonResponse(ok_message)
        error_message = {'status': 'error', 'action': 'login', 'error': 'Invalid credentials'}
        return JsonResponse(error_message, status=HTTPStatus.UNAUTHORIZED)


class SignupAPI(View):
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        if not (username and email and password):
            return JsonResponse({'error': 'Username and password are required'}, status=HTTPStatus.BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=HTTPStatus.BAD_REQUEST)
        User.objects.create_user(username=username, email=email, password=password)
        return JsonResponse({'message': 'User created successfully'}, status=HTTPStatus.CREATED)


@login_required()
@allow_methods(['GET'])
def get_user_detail(request):
    user = User.objects.get(username=request.user.username)
    return JsonResponse(
        {
            'username': user.username,
            'email': user.email,
            'last_login': user.last_login,
        })


def get_echo(_):
    ''' simple echo '''
    return HttpResponse(b'echo')


@allow_methods(['GET'])
def get_user_loggedin(request):
    if request.user and request.user.is_authenticated:
        return JsonResponse({'status': 'ok', 'loggedin': True})
    return JsonResponse({'status': 'ok', 'loggedin': False})
