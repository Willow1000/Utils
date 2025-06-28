
from requests.auth import HTTPBasicAuth
import json
import os
from .models import Product,Transactions
from dotenv import load_dotenv
from datetime import datetime
import base64
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
load_dotenv()


request = ""

def getAccessToken(request):
    consumer_key = os.getenv("MPESA_CONSUMER_KEY")
    consumer_secret = os.getenv("MPESA_CONSUMER_SECRET")
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    try:

        response = requests.get(api_url,auth=HTTPBasicAuth(consumer_key,consumer_secret))
        api_json_response = json.loads(response.text)
        valid_mpesa_access_token = api_json_response['access_token']
        if valid_mpesa_access_token:
            # print(valid_mpesa_access_token)
            return valid_mpesa_access_token
        else:

            print(f"API RETURNED THIS: {api_json_response}")    

    except Exception as e:
        print(f"An error occurred: {e}")  

import os
import base64
from datetime import datetime
from django.http import JsonResponse
import requests

def STKPayment(request):
    if request.method == "POST":
        try:
            access_token = getAccessToken(request)
            if not access_token or access_token == "YOUR_ACCESS_TOKEN_HERE":
                return JsonResponse({'error': 'Failed to retrieve access token'}, status=500)

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            shortcode = os.getenv("MPESA_SHORTCODE", "174379") # Use environment variable, fallback to default
            passkey = os.getenv("MPESA_PASSKEY")
            callback_url = os.getenv("MPESA_CALLBACK_URL", "https://yourdomain.com/callback/") # Make callback URL configurable

            if not passkey:
                return JsonResponse({'error': 'MPESA_PASSKEY environment variable not set'}, status=500)

            # Validate and sanitize phone number
            phone_number_raw = request.POST.get('phoneNumber', '')
            if not phone_number_raw:
                return JsonResponse({'error': 'Phone number is required'}, status=400)

            # Remove any non-digit characters and ensure it starts with 254
            phone = ''.join(filter(str.isdigit, phone_number_raw))
            if phone.startswith('0'):
                phone = '254' + phone[1:]
            elif not phone.startswith('254'):
                phone = '254' + phone
            
            if len(phone) != 12:
                return JsonResponse({'error': 'Invalid phone number format. Must be 12 digits starting with 254'}, status=400)

            # Validate and convert amount
            amount = request.POST.get('total_amount')
            product_id = request.POST.get('product_id')
            # print(product_id)
            # Generate password as per Safaricom documentation
            password = base64.b64encode((shortcode + passkey + timestamp).encode()).decode("utf-8")

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            
            # print(callback_url)
            if callback_url == "https://yourdomain.com/callback/":
                print("WARNING: MPESA_CALLBACK_URL is using a placeholder. Update it for production.")

            body = {
                "BusinessShortCode": shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": "1",
                "PartyA": phone,
                "PartyB": shortcode,
                "PhoneNumber": phone, # Use the customer's phone number here
                "CallBackURL": callback_url,
                "AccountReference": "Testaccount", # Consider making this dynamic
                "TransactionDesc": "Test" # Consider making this dynamic
            }

            response = requests.post("https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest", headers=headers, json=body) # Use json=body for automatic serialization
            # response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            # print(response.json())
            response_dict = response.json()
            # print(response_dict)
            checkout_request_id = response_dict.get('CheckoutRequestID')
            merchant_request_id = response_dict.get('MerchantRequestID')
            product = get_object_or_404(Product,id=product_id)
            start_time = request.POST.get('start_datetime')
            expiry_time = request.POST.get('expiry_datetime')
            Transactions.objects.create(
                checkout_request_id = checkout_request_id,
                merchant_request_id = merchant_request_id,
                amount = amount,
                product = product,
                start_time = start_time,
                expiry_time = expiry_time,
                phone_number = phone
            )
            
            return response_dict
        except requests.exceptions.RequestException as e:
            print(f"Network or API error occurred: {e}")
            return JsonResponse({'error': f'Network or API error: {e}'}, status=500)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return JsonResponse({'error': f'An unexpected error occurred: {e}'}, status=500)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


