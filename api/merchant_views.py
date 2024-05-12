import base64

from wbstorebackend.settings import DEBUG

from django.http import JsonResponse
from django.core.files.base import ContentFile

from .models import Merchandise
from .widgets import binarymd5
from .decorators import has_json_payload, login_required, allow_methods, \
        role_required


@allow_methods(['POST'])
@has_json_payload()
@login_required()
@role_required('merchant')
def post_insert_merchandise(request):
    form = request.json_payload
    if DEBUG:
        print(form)
    image_binary = base64.b64decode(form['image_description'])
    form['image_description'] = ContentFile(
            content=image_binary,
            name=binarymd5(image_binary))
    form['added_by_user'] = request.user
    Merchandise(**form).save()
    return JsonResponse({'status': 'merchandise saved'})
