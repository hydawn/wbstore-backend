from hashlib import md5
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
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


def paginate_queryset(queryset: QuerySet, per_page: int, page: int = 1):
    # Paginate the queryset
    paginator = Paginator(queryset, per_page)
    try:
        page_list = paginator.page(page)
    except PageNotAnInteger:
        page_list = paginator.page(1)
    except EmptyPage:
        page_list = paginator.page(paginator.num_pages)
    # Access the objects for the current page
    return page_list, paginator.num_pages, page_list.number


def query_merchandise_user(user: User, per_page: int, page_number: int) -> list[Merchandise]:
    ''' return Merchandise objects '''
    # Perform the query using Django's ORM
    queryset = Merchandise.objects.filter(added_by_user=user).order_by('online_date')
    return list(paginate_queryset(queryset, per_page, page_number)[0])


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


def search_merchandise(params: dict[str, str]) -> QuerySet:
    use_regex: bool = params.get('regex', 'False') in ['true', 'True']
    if params.get('name'):
        if use_regex:
            queryset = Merchandise.objects.filter(name__regex=params.get('name'))
        else:
            queryset = Merchandise.objects.filter(name__icontains=params.get('name'))
    else:
        queryset = Merchandise.objects.all()
    if params.get('text_description'):
        if use_regex:
            queryset = queryset.filter(text_description__regex=params.get('text_description'))
        else:
            queryset = queryset.filter(text_description__icontains=params.get('text_description'))
    if params.get('merchant'):
        if use_regex:
            queryset = queryset.filter(added_by_user__username__regex=params.get('merchant'))
        else:
            queryset = queryset.filter(added_by_user__username__icontains=params.get('merchant'))
    return queryset
