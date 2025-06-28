# 💰 M-Pesa STK Push Integration (Django)

A Django-based utility module for handling M-Pesa payments via STK Push. It provides a full flow from initiating payment, verifying transactions, handling callbacks, and storing transaction data securely.

---

## ⚙️ Features

- 🔐 Access token generation with Basic Auth
- 📲 Initiates M-Pesa STK Push requests
- 🧾 Handles real-time M-Pesa callbacks (success/failure)
- 🗃️ Stores transaction metadata in `MpesaTransaction` and `Transactions` models
- 🧼 Phone number validation & formatting
- 📄 Frontend-ready views (`PaymentView`, `MpesaReceiptView`)
- 🧪 Logs and prevents duplicate transactions

---

## 📁 Folder Structure
payment/
├── models.py
├── views.py
├── utils.py
├── templates/
│ └── payment/
│ ├── payment.html
│ └── receipt.html


---

## 🧠 How It Works

1. **Frontend calls `/pay/` with POST data** (phone number, amount, product ID, start/expiry time).
2. `STKPayment()` in `utils.py` fetches an access token and sends a request to Safaricom's STK Push API.
3. On M-Pesa callback, `mpesa_callback` captures the result and metadata, and stores it in `MpesaTransaction`.
4. Transaction validity is tracked via a `Transactions` model.
5. Receipt view allows authenticated users to fetch transaction info using the `CheckoutRequestID`.

---

## 📦 Environment Variables

Use a `.env` file or configure your environment with the following:

env
MPESA_CONSUMER_KEY=your_consumer_key
MPESA_CONSUMER_SECRET=your_consumer_secret
MPESA_SHORTCODE=174379  # or your Paybill
MPESA_PASSKEY=your_passkey
MPESA_CALLBACK_URL=https://yourdomain.com/callback/

⚠️ Warning: Do not use the placeholder callback in production. Replace "https://yourdomain.com/callback/".

POST /pay/
Content-Type: application/x-www-form-urlencoded

{
  "phoneNumber": "0712345678",
  "total_amount": "100",
  "product_id": "3",
  "start_datetime": "2025-06-28 10:00",
  "expiry_datetime": "2025-06-28 12:00"
}

If successful, redirects to:
GET /receipt/?checkout_request_id=<CheckoutRequestID>

📬 Callback Payload (Handled at /mpesa_callback/)
json
Copy
Edit
{
  "Body": {
    "stkCallback": {
      "MerchantRequestID": "...",
      "CheckoutRequestID": "...",
      "ResultCode": 0,
      "ResultDesc": "The service request is processed successfully.",
      "CallbackMetadata": {
        "Item": [
          {"Name": "Amount", "Value": 100},
          {"Name": "MpesaReceiptNumber", "Value": "NLJ7RTS1XP"},
          {"Name": "TransactionDate", "Value": 20250628103030},
          {"Name": "PhoneNumber", "Value": 254712345678}
        ]
      }
    }
  }
}
🧱 Models
MpesaTransaction
Field	Description
checkout_request_id	M-Pesa session identifier
result_code	0 for success
mpesa_receipt_number	Unique M-Pesa receipt number
amount	Paid amount
phone_number	User's phone number
created_at	Timestamp

Method:

python
Copy
Edit
def is_successful(self):
    return self.result_code == 0
Transactions
Tracks pending/completed payments related to a product.

Field	Description
product	FK to ParkingSpace
amount	Integer, transaction value
start_time	Parking start
expiry_time	Parking end
is_valid	Flag set True upon callback

🧩 Views Overview
View	Purpose
pay	Handles the POST to trigger STK Push
mpesa_callback	Webhook endpoint for M-Pesa to hit after payment
MpesaReceiptView	Displays transaction receipt based on ID
PaymentView	Renders initial payment form with amount & slot

✅ To Do / Improvements
Add proper phone validation for international formats

Allow dynamic AccountReference and TransactionDesc

Improve error logging (hook into Django’s logging module)

Add test cases or mock sandbox responses

Optionally: Encrypt sensitive fields (phone, receipt, etc.)

🛡️ Security Notes
Ensure .env variables are NEVER pushed to version control.

Set callback URL to HTTPS and verify request authenticity if needed.

Consider rate limiting the STK push request endpoint.

🤝 Contribution
Feel free to fork, raise issues, or suggest optimizations via PR.

📜 License
MIT — use, modify, break, and fix freely.




