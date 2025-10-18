from flask import Flask, render_template, redirect, request, jsonify
from uuid import uuid4
from phonepe.sdk.pg.payments.v2.standard_checkout_client import StandardCheckoutClient
from phonepe.sdk.pg.payments.v2.models.request.standard_checkout_pay_request import StandardCheckoutPayRequest
from phonepe.sdk.pg.common.models.request.meta_info import MetaInfo
from phonepe.sdk.pg.env import Env

app = Flask(__name__)

# PhonePe Configuration
client_id = "SU2508041810254120514281"
client_secret = "c99221ef-7d77-4f9f-88da-33960804b858"
client_version = "1"
env = Env.PRODUCTION
should_publish_events = False

# Initialize PhonePe client
client = StandardCheckoutClient.get_instance(
    client_id=client_id, 
    client_secret=client_secret, 
    client_version=client_version, 
    env=env, 
    should_publish_events=should_publish_events
)

# Plan pricing
PLAN_PRICES = {
    'silver': 1,
    'gold': 2,
    'platinum': 3
}

@app.route('/')
def home():
    """Serve the payment plans page"""
    return render_template('index.html')

@app.route('/api/create-payment/<plan>')
def create_payment(plan):
    """Generate payment link for selected plan"""
    try:
        # Validate plan
        if plan not in PLAN_PRICES:
            return jsonify({"error": "Invalid plan"}), 400
        
        # Get amount based on plan
        amount = PLAN_PRICES[plan] * 100
        
        # Generate unique order ID (must be <35 chars)
        unique_order_id = str(uuid4()).replace('-', '')[:32]
        
        # Set redirect URL (where user returns after payment)
        ui_redirect_url = "https://gov.nonexistential.dev/"
        
        # Create metadata
        meta_info = MetaInfo(udf1=plan, udf2=f"amount_{amount/100}", udf3="payment") 
        
        # Build payment request
        standard_pay_request = StandardCheckoutPayRequest.build_request(
            merchant_order_id=unique_order_id,
            amount=amount,
            redirect_url=ui_redirect_url,
            meta_info=meta_info
        )
        
        # Get payment response
        standard_pay_response = client.pay(standard_pay_request)
        checkout_page_url = standard_pay_response.redirect_url
        
        # Log for debugging
        print(f"Payment link created for {plan} plan (₹{amount/100})")
        print(f"Order ID: {unique_order_id}")
        print(f"Checkout URL: {checkout_page_url}")
        
        # Return payment link as JSON
        return jsonify({
            "success": True,
            "payment_url": checkout_page_url,
            "order_id": unique_order_id,
            "plan": plan,
            "amount": amount / 100
        })
    
    except Exception as e:
        print(f"Error creating payment: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)