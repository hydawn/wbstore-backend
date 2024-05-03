#from django.shortcuts import render

import json
import base64
from http import HTTPStatus

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.csrf import get_token

from .decorators import login_required, allow_methods, role_required

from wbstorebackend.settings import DEBUG
from .models import Merchandise, ShoppingCart, UserDetail
from .widgets import get_user_role, binarymd5, query_merchandise_name


class CsrfTokenAPI(View):
    def get(self, request):
        return JsonResponse({'csrfToken': get_token(request)})


class LoginAPI(View):
    def post(self, request: WSGIRequest):
        print(f'got post request')
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
            ok_message = {'status': 'ok', 'action': 'login', 'username': username, 'role': get_user_role(username)}
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
        role = post_data.get('role')
        if not (username and email and password and role):
            return JsonResponse({'error': 'Username, password and email and role are required'}, status=HTTPStatus.BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=HTTPStatus.BAD_REQUEST)
        new_user = User.objects.create_user(username=username, email=email, password=password)
        user_detail = UserDetail(user=new_user, role_customer=role == 'customer', role_merchant=role == 'merchant')
        user_detail.save()
        return JsonResponse({'message': 'User created successfully'}, status=HTTPStatus.CREATED)


@allow_methods(['GET'])
@login_required()
def get_user_detail(request):
    user = User.objects.get(username=request.user.username)
    return JsonResponse(
        {
            'username': user.username,
            'email': user.email,
            'last_login': user.last_login,
            'role': get_user_role(user.username),
        })


def get_echo(_):
    ''' simple echo '''
    return HttpResponse(b'echo')


@allow_methods(['GET'])
def get_user_loggedin(request):
    if request.user and request.user.is_authenticated:
        return JsonResponse({'status': 'ok', 'loggedin': True, 'role': get_user_role(request.user.username)})
    return JsonResponse({'status': 'ok', 'loggedin': False})

@allow_methods(['POST'])
@login_required()
def post_logout(request):
    ''' log the user out '''
    logout(request)
    return JsonResponse({'status': 'ok'})


@allow_methods(['POST'])
@login_required()
@role_required('merchant')
def post_insert_merchandise(request):
    form = json.loads(request.body)
    if DEBUG:
        print(form)
    image_binary = base64.b64decode(form['image_description'])
    form['image_description'] = ContentFile(
            content=image_binary,
            name=binarymd5(image_binary))
    form['added_by_user'] = request.user
    Merchandise(**form).save()
    return JsonResponse({'status': 'on dev'})


@allow_methods(['GET'])
@login_required()
def get_search_merchandise(request):
    '''
    return info about merchandise
    require a query
    query username or merchandise_name
    count = 10 by default
    '''
    form = json.loads(request.body)
    print(form)
    if 'merchandise_name' in form:
        return JsonResponse({'status': 'ok', 'data': [i.to_json_dict() for i in query_merchandise_name(form['merchandise_name'], form['per_page'], form['page_number'])]})
    elif 'username' in form:
        return JsonResponse({'status': 'error', 'error': 'not implemented yet'}, status=HTTPStatus.BAD_REQUEST)
    # which merchandise? merchant id?


@allow_methods(['POST'])
@login_required()
@role_required('customer')
def post_add_to_shopping_chart(request):
    form = json.loads(request.body)
       # well well well, how do I get this?
    merch_query_list = Merchandise.objects.filter(pk=form['merchandise_id'])
    if len(merch_query_list) == 0:
        return JsonResponse({'status': 'error', 'error': 'no such merchandise'}, status=HTTPStatus.BAD_REQUEST)
    merch = merch_query_list[0]
    if ShoppingCart.objects.filter(user=request.user).filter(merchandise=merch):
        return JsonResponse({'status': 'ok', 'message': 'already added to chopping cart'})
    ShoppingCart(user=request.user, merchandise=merch).save()
    return JsonResponse({'status': 'ok', 'message': 'added to shopping cart'})
