# TODO: round 2 for every price before inserting
from http import HTTPStatus

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.csrf import get_token

import logging

from .decorators import has_json_payload, login_required, allow_methods, \
        merchandise_exist, role_required, runningorder_exist, \
        has_query_params, user_can_view_runningorder, \
        user_can_modify_runningorder, get_with_pages

from wbstorebackend.settings import DEBUG
from .models import UserDetail, RunningOrder
from .widgets import get_user_role, make_order_form, paginate_queryset, \
        search_merchandise


logger = logging.getLogger('django')


class CsrfTokenAPI(View):
    def get(self, request):
        return JsonResponse({'csrfToken': get_token(request)})


@allow_methods(['POST'])
@has_json_payload()
def post_login(request):
    username = request.json_payload.get('username')
    password = request.json_payload.get('password')
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


@allow_methods(['POST'])
@has_json_payload()
def post_signup(request):
    username = request.json_payload.get('username')
    password = request.json_payload.get('password')
    email = request.json_payload.get('email')
    role = request.json_payload.get('role')
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


@allow_methods(['GET'])
@has_query_params(['per_page', 'page_number'])
@get_with_pages()
@login_required()
def get_search_merchandise(request):
    '''
    return info about merchandise
    require a query
    query username or merchandise_name
    count = 10 by default
    '''
    logger.info('search merchandise with params: %s', request.GET)
    queryset = search_merchandise(request.GET)
    page, total_page, current_page = paginate_queryset(queryset, request.per_page, request.page_number)
    return JsonResponse({'status': 'ok', 'data': {
        'data_list': [i.to_json_dict() for i in page],
        'current_page': current_page,
        'total_page': total_page
    }})


@allow_methods(['POST'])
@has_json_payload()
@login_required()
@role_required('customer')
@merchandise_exist('post')
def post_make_order(request):
    ''' a user creating an order '''
    form = make_order_form(request, status_incart=False)
    if isinstance(form, JsonResponse):
        return form
    new_order = RunningOrder(**form)
    new_order.save()
    if DEBUG:
        print(f'get new order {new_order.id}')
    return JsonResponse({'status': 'ok', 'data': {'orderId': new_order.id}})


@allow_methods(['POST'])
@has_json_payload()
@login_required()
@role_required('customer')
@runningorder_exist('post')
@user_can_view_runningorder()
@user_can_modify_runningorder()
def post_customer_change_order(request):
    ''' user changing an order make, paid, cancel '''
    status = request.runningorder.status_end
    if status not in ['running']:
        return JsonResponse({'status': 'error', 'error': f'no action is to be taken on a order in a state {status}'})
    if request.json_payload['action'] == 'pay':
        if request.runningorder.status_paid:
            return JsonResponse({'status': 'alert', 'alert': 'already paid'})
        request.runningorder.status_paid = True
    elif request.json_payload['action'] == 'cancel':
        if request.runningorder.status_cancelling:
            return JsonResponse({'status': 'alert', 'alert': 'already cancelled'})
        request.runningorder.status_cancelling = True
    elif request.json_payload['action'] == 'finish':
        if not request.runningorder.status_taken:
            return JsonResponse(
                    {'status': 'error', 'error': 'can not finish: order not taken yet'},
                    status=HTTPStatus)
        request.runningorder.status_end = 'finished'
    request.runningorder.save()
    return JsonResponse({'status': 'ok'})


@allow_methods(['GET'])
@has_query_params(['merchandise_id'])
@login_required()
@merchandise_exist('get')
def get_get_merchandise(request):
    return JsonResponse({'status': 'ok', 'data': request.merchandise.to_json_dict()})


@allow_methods(['GET'])
@has_query_params(['runningorder_id'])
@login_required()
@runningorder_exist('get')
@user_can_view_runningorder()
def get_get_order(request):
    return JsonResponse({'status': 'ok', 'data': request.runningorder.to_json_dict()})


@allow_methods(['GET'])
@has_query_params(['per_page', 'page_number'])
@login_required()
@role_required('customer')
def get_search_customer_order(request):
    per_page = int(request.GET.get('per_page'))
    page_number = int(request.GET.get('page_number'))
    queryset = RunningOrder.objects.filter(user=request.user, status_incart=False).order_by('added_date')
    total_count = len(queryset)
    queryset, total_page, current_page = paginate_queryset(queryset, per_page, page_number)
    return JsonResponse({
        'status': 'ok',
        'data': {
                'order_list': [i.to_json_dict() for i in queryset],
                'total_count': total_count,
                'current_page': current_page,
                'total_page': total_page
            }})
