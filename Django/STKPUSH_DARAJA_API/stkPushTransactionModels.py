from django.db import models
from Home.models import ParkingSpace
class MpesaTransaction(models.Model):
    merchant_request_id = models.CharField(max_length=100)
    checkout_request_id = models.CharField(max_length=100,unique=True)
    
    result_code = models.IntegerField()
    result_desc = models.TextField()

    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mpesa_receipt_number = models.CharField(max_length=50, null=True, blank=True,unique=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def is_successful(self):
        return self.result_code == 0

    def __str__(self):
        return f"{self.mpesa_receipt_number or 'N/A'} - {self.amount or '0'} KES"


class Transactions(models.Model):
    checkout_request_id = models.CharField(max_length=100,unique=True)
    merchant_request_id = models.CharField(max_length=100)
    amount = models.IntegerField()
    product= models.ForeignKey(ParkingSpace,on_delete=models.CASCADE)
    start_time = models.CharField(max_length=25)
    phone_number = models.CharField(max_length=12)
    expiry_time = models.CharField(max_length=25)
    is_valid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add = True, blank=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True,null=True)


    def __str__(self):
        return f"{self.checkout_request_id} {self.merchant_request_id}"