import base64
from http import HTTPStatus

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.csrf import get_token

from .decorators import has_json_payload, login_required, allow_methods, \
        merchandise_exist, role_required, runningorder_exist, \
        has_query_params

from wbstorebackend.settings import DEBUG
from .models import DeadOrder, Merchandise, ShoppingCart, UserDetail, \
        RunningOrder, deadorder_from_runningorder
from .widgets import get_user_role, binarymd5, query_merchandise_name, \
        paginate_queryset


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
@has_query_params(['merchandise_name', 'per_page', 'page_number'])
@login_required()
def get_search_merchandise(request):
    '''
    return info about merchandise
    require a query
    query username or merchandise_name
    count = 10 by default
    '''
    merchandise_name = request.GET.get('merchandise_name')
    per_page = int(request.GET.get('per_page'))
    page_number = int(request.GET.get('page_number'))
    return JsonResponse({'status': 'ok', 'data': [
        i.to_json_dict()
        for i in query_merchandise_name(merchandise_name, per_page, page_number)]})
    # if 'username' in request.json_payload:
    #     return JsonResponse({'status': 'error', 'error': 'not implemented yet'}, status=HTTPStatus.BAD_REQUEST)
    # which merchandise? merchant id?


@allow_methods(['POST'])
@has_json_payload()
@login_required()
@role_required('customer')
@merchandise_exist('post')
def post_add_to_shopping_chart(request):
    user_cart = ShoppingCart.objects.filter(user=request.user)
    if len(user_cart.filter(merchandise=request.merchandise)) != 0:
        return JsonResponse({'status': 'ok', 'message': 'already added to chopping cart'})
    ShoppingCart(user=request.user, merchandise=request.merchandise).save()
    return JsonResponse({'status': 'ok', 'message': 'added to shopping cart'})


@allow_methods(['GET'])
@has_query_params(['per_page', 'page_number'])
@login_required()
@role_required('customer')
def get_my_shopping_chart(request):
    ''' return a list of merch '''
    query_set = ShoppingCart.objects.filter(user=request.user).order_by('added_date')
    per_page = int(request.GET.get('per_page'))
    page_number = int(request.GET.get('page_number'))
    merch_list = paginate_queryset(query_set, per_page, page_number)
    return JsonResponse({'status': 'ok', 'data':[i.merchandise.to_json_dict() for i in merch_list]})


@allow_methods(['POST'])
@has_json_payload()
@login_required()
@role_required('customer')
@merchandise_exist('post')
def post_make_order(request):
    ''' a user creating an order '''
    form = request.json_payload
    if DEBUG:
        print(f'get form {form}')
    form['user'] = request.user
    form['merchandise'] = request.merchandise
    form.pop('merchandise_id')
    new_order = RunningOrder(**form)
    new_order.save()
    if DEBUG:
        print(f'get new order {new_order.id}')
    return JsonResponse({'status': 'ok', 'data': {'orderId': new_order.id}})


@allow_methods(['GET'])
@login_required()
@role_required('customer')
def get_customer_running_orders(request):
    ''' get running orders '''
    queryset = RunningOrder.objects.filter(user=request.user)
    return JsonResponse({'status': 'ok', 'data': [i.to_json_dict() for i in queryset]})


@allow_methods(['POST'])
@has_json_payload()
@login_required()
@role_required('customer')
@runningorder_exist('post')
def post_customer_change_order(request):
    ''' user changing an order make, paid, cancel '''
    if request.json_payload['action'] == 'pay':
        if request.runningorder.status_paid:
            return JsonResponse({'status': 'alert', 'alert': 'already paid'})
        request.runningorder.status_paid = True
    elif request.json_payload['action'] == 'cancel':
        if request.runningorder.status_cancelling:
            return JsonResponse({'status': 'alert', 'alert': 'already cancelled'})
        request.runningorder.status_cancelling = True
    return JsonResponse({'status': 'ok'})


@allow_methods(['POST'])
@has_json_payload()
@login_required()
@role_required('merchant')
@runningorder_exist('post')
def post_merchant_change_order(request):
    ''' user changing an order make, paid, cancel '''
    if request.json_payload['action'] == 'take':
        if request.runningorder.status_taken:
            return JsonResponse({'status': 'alert', 'alert': 'already taken'})
        request.runningorder.status_taken = True
    elif request.json_payload['action'] == 'accept cancel':
        if not request.runningorder.status_cancelling:
            return JsonResponse({'status': 'error', 'error': 'not cancelling'}, status=HTTPStatus.BAD_REQUEST)
        deadorder_from_runningorder(request.runningorder, 'cancelled').save()
        request.runningorder.delete()
    return JsonResponse({'status': 'ok'})


@allow_methods(['POST'])
@has_json_payload()
@login_required()
@role_required('merchant')
@runningorder_exist('post')
def post_take_order(request):
    ''' a merchant taking an order -- set the order state to taken '''
    form = request.json_payload
    form['user'] = request.user
    form['merchandise'] = request.merchandise
    RunningOrder(**form).save()
