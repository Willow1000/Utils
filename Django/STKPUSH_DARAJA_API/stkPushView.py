from django.shortcuts import redirect
from django.http import HttpResponseNotAllowed,JsonResponse
from django.template import loader
from .utils import STKPayment
from django.views.decorators.csrf import csrf_exempt
from .models import MpesaTransaction, Transactions
from django.shortcuts import get_object_or_404
from.models import Product
from django.urls import reverse
import json
import traceback
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from time import sleep


def pay(request):
    if request.method == 'POST':
        response = STKPayment(request)
        checkout_request_id = response.get('CheckoutRequestID')
        template = loader.get_template("payment/payment.html")
        sleep(10)
        base_url = reverse('receipt')  # or any named URL
        
        url = f"{base_url}?checkout_request_id={checkout_request_id}"
        return redirect(url)
    else:
        HttpResponseNotAllowed(['GET'])

@csrf_exempt
def mpesa_callback(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests allowed"}, status=405)

    try:
        data = json.loads(request.body)
        stk_callback = data["Body"]["stkCallback"]

        result_code = stk_callback["ResultCode"]
        result_desc = stk_callback["ResultDesc"]
        merchant_request_id = stk_callback["MerchantRequestID"]
        checkout_request_id = stk_callback["CheckoutRequestID"]
        transaction = get_object_or_404(Transactions, checkout_request_id = checkout_request_id)
        if result_code == 0:
            metadata = {item["Name"]: item.get("Value") for item in stk_callback.get("CallbackMetadata", {}).get("Item", [])}

            amount = metadata.get("Amount")
            receipt = metadata.get("MpesaReceiptNumber")
            # prevent duplicate saving
            if receipt and MpesaTransaction.objects.filter(mpesa_receipt_number=receipt).exists():
                return JsonResponse({"ResultCode": 0, "ResultDesc": "Already received"})

            trans_date_raw = metadata.get("TransactionDate")
            phone = metadata.get("PhoneNumber")

            MpesaTransaction.objects.create(
                merchant_request_id=merchant_request_id,
                checkout_request_id=checkout_request_id,
                result_code=result_code,
                result_desc=result_desc,
                amount=amount,
                mpesa_receipt_number=receipt,
                phone_number=phone
            )
            
            transaction.is_valid = True
            transaction.save()
        else:
            # transaction.delete()
            MpesaTransaction.objects.create(
                merchant_request_id=merchant_request_id,
                checkout_request_id=checkout_request_id,
                result_code=result_code,
                result_desc=result_desc,
            )

        print(stk_Callback)
        return JsonResponse({"ResultCode": 0, "ResultDesc": "Callback received successfully"})

    except Exception as e:
        logger.error("M-Pesa callback error: %s", str(e))
        logger.error(traceback.format_exc())  # Full traceback
        return JsonResponse({"error": "Internal Server Error"}, status=500)

class MpesaReceiptView(LoginRequiredMixin,TemplateView):
    model = Transactions
    template_name = "payment/receipt.html"
    login_url = reverse_lazy('login')

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        checkout_request_id = self.request.GET.get("checkout_request_id")
        transaction = get_object_or_404(Transactions, checkout_request_id = checkout_request_id)
        context['transaction'] = transaction
        return context

class PaymentView(LoginRequiredMixin,TemplateView):
    template_name = "payment/payment.html"
    login_url = reverse_lazy('login')
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        amount = self.request.GET.get('amount')
        # print(self.request.GET)
        slot_id = self.request.GET.get("slot")
        product = get_object_or_404(Product,id=int(slot_id))
      
        context['amount'] = amount
        context['product_id'] = product.id
        return context