''' view func for merchant '''
import base64

from django.http import JsonResponse
from django.core.files.base import ContentFile

from .models import Merchandise, RunningOrder
from .widgets import binarymd5, query_merchandise_user, paginate_queryset
from .decorators import get_with_pages, has_json_payload, login_required, allow_methods, \
        role_required, runningorder_exist, user_can_view_runningorder, \
        user_can_modify_runningorder, has_query_params


@allow_methods(['POST'])
@has_json_payload()
@login_required()
@role_required('merchant')
def post_insert_merchandise(request):
    form = request.json_payload
    image_binary = base64.b64decode(form['image_description'])
    form['image_description'] = ContentFile(
            content=image_binary,
            name=binarymd5(image_binary))
    form['added_by_user'] = request.user
    Merchandise(**form).save()
    return JsonResponse({'status': 'merchandise saved'})


# TODO: more checks on the backend:
# order status/order number valid, that sort of thing
@allow_methods(['POST'])
@has_json_payload()
@login_required()
@role_required('merchant')
@runningorder_exist('post')
@user_can_view_runningorder()
@user_can_modify_runningorder()
def post_merchant_change_order(request):
    ''' user changing an order make, paid, cancel '''
    status = request.runningorder.status_end
    if status not in ['running']:
        return JsonResponse({'status': 'error', 'error': f'no action is to be taken on a order in a state {status}'})
    action = request.json_payload['action']
    if action == 'take':
        if request.runningorder.status_taken:
            return JsonResponse({'status': 'alert', 'alert': 'already taken'})
        request.runningorder.status_taken = True
        request.runningorder.save()
    elif action == 'accept cancel':
        if not request.runningorder.status_cancelling:
            return JsonResponse({'status': 'error', 'error': 'not cancelling'})
        request.runningorder.status_end = 'cancelled'
        request.runningorder.save()
    return JsonResponse({'status': 'ok'})


@allow_methods(['GET'])
@has_query_params(['per_page', 'page_number'])
@get_with_pages()
@login_required()
@role_required('merchant')
def get_get_merchant_merchandise(request):
    '''
    return info about merchandise
    require a query
    query username or merchandise_name
    count = 10 by default
    '''
    return JsonResponse({'status': 'ok', 'data': [
        i.to_json_dict()
        for i in query_merchandise_user(request.user, request.per_page, request.page_number)]})


@allow_methods(['GET'])
@has_query_params(['per_page', 'page_number'])
@get_with_pages()
@login_required()
@role_required('merchant')
def get_search_merchant_order(request):
    '''
    get merchant orders
    '''
    # select * from runningorder where merchandise in (select * from merchandise where added_by_user == given_user);
    queryset = RunningOrder.objects.filter(
            merchandise__in=Merchandise.objects.filter(
                added_by_user=request.user
            )).order_by('added_date')
    total_count = len(queryset)
    queryset, total_page, current_page = paginate_queryset(queryset, request.per_page, request.page_number)
    return JsonResponse({
        'status': 'ok',
        'data': {
            'order_list': [i.to_json_dict() for i in queryset],
            'total_page': total_page,
            'current_page': current_page,
            'total_count': total_count
        }})
