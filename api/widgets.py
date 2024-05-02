from django.contrib.auth.models import User
from .models import UserDetail

def get_user_role(username: str) -> str:
    user = User.objects.get(username=username)
    user_detail = UserDetail.objects.get(user_id=user.id)
    if user_detail.role_merchant:
        return 'merchant'
    return 'customer'