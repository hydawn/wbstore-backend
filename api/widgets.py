from hashlib import md5
from django.core.paginator import Paginator

from django.contrib.auth.models import User
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


def query_merchandise_name(merchandise_name: str, per_page: int, page_number: int = 1) -> list[Merchandise]:
    ''' return Merchandise objects '''
    # Perform the query using Django's ORM
    queryset = Merchandise.objects.filter(name__icontains=merchandise_name).order_by('online_date')

    # Paginate the queryset
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(page_number)

    # Access the objects for the current page
    return page_obj.object_list
