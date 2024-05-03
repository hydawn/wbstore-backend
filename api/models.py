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
            'id': self.id,
            'name': self.name,
            'text_description': self.text_description,
            'image_description': image_base64,
            'price': self.price,
            'online_data': str(self.online_date),
            'stock_inventory': self.stock_inventory,
            'added_by_user': self.added_by_user.username,
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

    def __str___(self):
        return str(self.user) + str(self.merchandise)


class FavoriteMerchandise(models.Model):
    objects: models.Manager
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    merchandise = models.ForeignKey(Merchandise, on_delete=models.CASCADE)


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


class DeadOrder(models.Model):
    ''' orders that's finished for all sorts of reasons '''
    objects: models.Manager
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    merchandise = models.ForeignKey(Merchandise, on_delete=models.CASCADE)
    count = models.IntegerField()
    total_price = models.IntegerField()
    # the order can be cancelled by the customer or the merchant
    status_cancelled = models.BooleanField()
    status_finished = models.BooleanField()
