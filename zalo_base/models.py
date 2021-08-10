from django.db import models
from django.db.models import fields


class ZaloUser(models.Model):

    name = models.CharField(max_length=200, null=True, blank=True)
    user_id = models.CharField(max_length=200, unique=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    district = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    regist_payment_phone = models.CharField(max_length=30, null=True, blank=True)
    ward = models.CharField(max_length=200, null=True, blank=True)
    payment_code = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return "[%s] %s - %s" % (self.user_id,self.name, self.phone)

