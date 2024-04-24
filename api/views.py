#from django.shortcuts import render

import json
from http import HTTPStatus

from django.contrib.auth import authenticate, login, logout
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
        if request.content_type != 'application/json':
            return JsonResponse({'status': 'error', 'error': 'content_type must be application/json'}, status=HTTPStatus.BAD_REQUEST)
        try:
            post_data = json.loads(request.body)
        except json.JSONDecodeError as jderror:
            return JsonResponse({'status': 'error', 'error': f'JSONDecodeError: {jderror}'}, status=HTTPStatus.BAD_REQUEST)
        username = post_data.get('username')
        password = post_data.get('password')
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
        if request.content_type != 'application/json':
            return JsonResponse({'status': 'error', 'error': 'content_type must be application/json'}, status=HTTPStatus.BAD_REQUEST)
        try:
            post_data = json.loads(request.body)
        except json.JSONDecodeError as jderror:
            return JsonResponse({'status': 'error', 'error': f'JSONDecodeError: {jderror}'}, status=HTTPStatus.BAD_REQUEST)
        username = post_data.get('username')
        password = post_data.get('password')
        email = post_data.get('email')
        if not (username and email and password):
            return JsonResponse({'error': 'Username, password and email are required'}, status=HTTPStatus.BAD_REQUEST)
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

@allow_methods(['POST'])
@login_required()
def post_logout(request):
    ''' log the user out '''
    logout(request)
    return JsonResponse({'status': 'ok'})
