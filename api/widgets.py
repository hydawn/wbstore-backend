from hashlib import md5
from django.core.paginator import Paginator
from django.http import JsonResponse

from django.contrib.auth.models import User
from django.db.models import QuerySet
from .models import UserDetail, Merchandise


def get_user_role(username: str) -> str:
    user = User.objects.get(username=username)
    user_detail = UserDetail.objects.get(user_id=user.id)
    if user_detail.role_merchant:
        return 'merchant'
    return 'customer'


def binarymd5(binstr: bytes) -> str:
    ''' return the hexdigest of a binaydata in python str '''
    return md5(binstr).hexdigest()


def paginate_queryset(queryset: QuerySet, per_page: int, page_number: int = 1):
    # Paginate the queryset
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(page_number)

    # Access the objects for the current page
    return page_obj.object_list


def query_merchandise_name(merchandise_name: str, per_page: int, page_number: int) -> list[Merchandise]:
    ''' return Merchandise objects '''
    # Perform the query using Django's ORM
    queryset = Merchandise.objects.filter(name__regex=merchandise_name).order_by('online_date')
    return paginate_queryset(queryset, per_page, page_number)


def query_merchandise_user(user: User, per_page: int, page_number: int) -> list[Merchandise]:
    ''' return Merchandise objects '''
    # Perform the query using Django's ORM
    queryset = Merchandise.objects.filter(added_by_user=user).order_by('online_date')
    return paginate_queryset(queryset, per_page, page_number)


def make_order_form(request, status_incart: bool=False) -> JsonResponse | dict:
    form = request.json_payload
    form['user'] = request.user
    form['merchandise'] = request.merchandise
    form['status_incart'] = status_incart
    form.pop('merchandise_id')
    try:
        form['count'] = int(form['count'])
        if form['count'] <= 0:
            return JsonResponse({'status': 'error', 'error': 'count of merchant less than 1 is not accepted'})
        form['total_price'] = round(float(form['total_price']), 2)
    except ValueError as err:
        return JsonResponse({'status': 'error', 'error': f'error in casting value: {err}'})
    return form
