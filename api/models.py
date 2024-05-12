import base64

from django.contrib.auth.models import User
from django.db import models


class UserDetail(models.Model):
    objects: models.Manager
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role_customer = models.BooleanField(default=True)
    role_merchant = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Merchandise(models.Model):
    objects: models.Manager
    name = models.CharField(max_length=512)
    text_description = models.CharField(max_length=4096, null=True)
    image_description = models.ImageField(upload_to='images/', null=True)
    price = models.FloatField()
    online_date = models.DateTimeField("date put online", auto_now_add=True)
    stock_inventory = models.IntegerField()
    added_by_user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)[:12]

    def to_json_dict(self) -> dict:
        with open(self.image_description.name, 'rb') as file:
            image_base64 = base64.b64encode(file.read()).decode('utf-8')
        return {
            'id': str(self.id),
            'name': self.name,
            'text_description': self.text_description,
            'image_description': image_base64,
            'price': self.price,
            'online_date': str(self.online_date),
            'stock_inventory': self.stock_inventory,
            'added_by_user': self.added_by_user.username,
            'added_by_user_id': str(self.added_by_user.id),
            }


class MerchandiseDetail(models.Model):
    objects: models.Manager
    merchandise = models.OneToOneField(Merchandise, on_delete=models.CASCADE)
    publisher = models.CharField(max_length=512, null=True)
    date_published = models.CharField(max_length=512, null=True)
    ISBN = models.CharField(max_length=512, null=True)
    authors = models.CharField(max_length=512, null=True)

    def __str__(self):
        return str(self.merchandise)


class ShoppingCart(models.Model):
    objects: models.Manager
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    merchandise = models.ForeignKey(Merchandise, on_delete=models.CASCADE)
    added_date = models.DateTimeField("date added", auto_now_add=True)

    def __str___(self):
        return str(self.user) + str(self.merchandise)


class FavoriteMerchandise(models.Model):
    objects: models.Manager
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    merchandise = models.ForeignKey(Merchandise, on_delete=models.CASCADE)
    added_date = models.DateTimeField("date added", auto_now_add=True)


class RunningOrder(models.Model):
    ''' orders that's still going '''
    # class OrderStatus(models.TextChoices):
    #     # order created, but no payments is done
    #     CREATED = 'CREATED', 'CREATED'
    #     # the customer created and payed for the order
    #     ISSUED = 'ISSUED', 'ISSUED'
    #     # the order is taken by the merchant
    #     TAKEN = 'TAKEN', 'TAKEN'
    #     # the customer is cancelling the order
    #     CANCELLING = 'CANCELLING', 'CANCELLING'
    #     # the order is cancelled
    #     CANCELLED = 'CANCELLED', 'CANCELLED'
    #     # the order is finished
    #     FINISHED = 'FINISHED', 'FINISHED'
    objects: models.Manager
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    merchandise = models.ForeignKey(Merchandise, on_delete=models.CASCADE)
    count = models.IntegerField()
    total_price = models.IntegerField()
    # whether the customer has paid the order
    status_paid = models.BooleanField()
    # whether the merchant has taken the order
    status_taken = models.BooleanField()
    # whether the customer wants to cancel the order
    status_cancelling = models.BooleanField()
    added_date = models.DateTimeField("date added", auto_now_add=True)

    def to_json_dict(self):
        return {
                'id': str(self.id),
                'username': self.user.username,
                'user_id': str(self.user.id),
                'merchandise_id': str(self.merchandise.id),
                'count': self.count,
                'total_price': self.total_price,
                'status_paid': self.status_paid,
                'status_taken': self.status_taken,
                'status_cancelling': self.status_cancelling,
                'added_date': str(self.added_date),
                }


class DeadOrder(models.Model):
    ''' orders that's finished for all sorts of reasons '''
    objects: models.Manager
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    merchandise = models.ForeignKey(Merchandise, on_delete=models.CASCADE)
    count = models.IntegerField()
    total_price = models.IntegerField()
    # the order can be cancelled or finished
    status = models.CharField(max_length=64)
    running_added_date = models.DateTimeField("date added when it's running")
    added_date = models.DateTimeField("date added", auto_now_add=True)


def deadorder_from_runningorder(order: RunningOrder, status: str) -> DeadOrder:
    return DeadOrder(
            user=order.user,
            merchandise=order.merchandise,
            count=order.count,
            total_price=order.total_price,
            status=status,
            running_added_date=order.added_date
            )
