from http import HTTPStatus
from django.http import JsonResponse

from .models import RunningOrder
from .decorators import has_json_payload, login_required, allow_methods, \
        merchandise_exist, role_required, runningorder_exist, \
        has_query_params, user_can_view_runningorder, \
        user_can_modify_runningorder
from .widgets import make_order_form, paginate_queryset


@allow_methods(['POST'])
@has_json_payload()
@login_required()
@role_required('customer')
@merchandise_exist('post')
def post_add_to_shopping_cart(request):
    user_cart = RunningOrder.objects.filter(user=request.user, status_incart=True)
    if len(user_cart.filter(merchandise=request.merchandise)) != 0:
        return JsonResponse({'status': 'ok', 'message': 'already added to shopping cart'})
    form = make_order_form(request, True)
    if isinstance(form, JsonResponse):
        return form
    RunningOrder(**form).save()
    return JsonResponse({'status': 'ok', 'message': 'added to shopping cart'})


@allow_methods(['GET'])
@has_query_params(['per_page', 'page_number'])
@login_required()
@role_required('customer')
def get_get_shopping_cart(request):
    ''' return a list of merch '''
    query_set = RunningOrder.objects.filter(user=request.user, status_incart=True).order_by('added_date')
    total_count = len(query_set)
    per_page = int(request.GET.get('per_page'))
    page_number = int(request.GET.get('page_number'))
    query_set = paginate_queryset(query_set, per_page, page_number)
    return JsonResponse({
        'status': 'ok',
        'data': {
            'cart_list': [i.to_json_dict() for i in query_set],
            'total_count': total_count
        }})


@allow_methods(['POST'])
@has_json_payload()
@login_required()
@role_required('customer')
@runningorder_exist('post')
def post_change_shopping_cart(request):
    order = request.runningorder
    if order.user != request.user:
        return JsonResponse({'status': 'error', 'error': 'user not authorised to alter this chopping cart'}, status=HTTPStatus.BAD_REQUEST)
    action = request.json_payload['action']
    # means make the cart an order
    if action == 'order':
        order.status_incart = False
        order.save()
        return JsonResponse({'status': 'ok', 'data': {'orderId': order.id} })
    if action == 'delete':
        order.delete()
    else:
        return JsonResponse({'status': 'error', 'error': f'no such action: {action}'}, status=HTTPStatus.BAD_REQUEST)
    return JsonResponse({'status': 'ok'})


@allow_methods(['GET'])
@has_query_params(['merchandise_id'])
@login_required()
@role_required('customer')
@merchandise_exist('get')
def get_check_shopping_cart(request):
    user_cart = RunningOrder.objects.filter(user=request.user, merchandise=request.merchandise, status_incart=True)
    if len(user_cart) != 0:
        return JsonResponse({'status': 'ok', 'message': 'exist in shopping cart'})
    return JsonResponse({'status': 'warning', 'warning': 'not in shopping cart'})
