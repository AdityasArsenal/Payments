from flask import Flask, render_template, redirect, request, jsonify
from uuid import uuid4
from phonepe.sdk.pg.payments.v2.standard_checkout_client import StandardCheckoutClient
from phonepe.sdk.pg.payments.v2.models.request.standard_checkout_pay_request import StandardCheckoutPayRequest
from phonepe.sdk.pg.common.models.request.meta_info import MetaInfo
from phonepe.sdk.pg.env import Env
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from config.env if it exists
load_dotenv('config.env')

app = Flask(__name__)

# PhonePe Configuration - Use environment variables for production
client_id = os.getenv("PHONEPE_CLIENT_ID", "SU2508041810254120514281")
client_secret = os.getenv("PHONEPE_CLIENT_SECRET", "c99221ef-7d77-4f9f-88da-33960804b858")
client_version = os.getenv("PHONEPE_CLIENT_VERSION", "1")
env = Env.PRODUCTION if os.getenv("PHONEPE_ENV", "PRODUCTION") == "PRODUCTION" else Env.UAT
should_publish_events = False

# Base URL for redirects (override in production)
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

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
        ui_redirect_url = f"{BASE_URL}/payment-callback"
        
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

@app.route('/api/check-payment-status/<order_id>')
def check_payment_status(order_id):
    """Check the status of a payment by order ID"""
    try:
        # Get order status from PhonePe
        response = client.get_order_status(order_id, details=False)
        
        # Extract payment details
        state = response.state
        
        # Log to console
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*60}")
        print(f"[{timestamp}] PAYMENT STATUS CHECK")
        print(f"{'='*60}")
        print(f"Order ID: {order_id}")
        print(f"Status: {state}")
        print(f"{'='*60}\n")
        
        return jsonify({
            "success": True,
            "order_id": order_id,
            "status": state,
            "timestamp": timestamp
        })
    
    except Exception as e:
        print(f"Error checking payment status: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/payment-callback')
def payment_callback():
    """Handle redirect after payment completion"""
    # PhonePe sends the merchant_order_id as a query parameter
    order_id = request.args.get('merchantOrderId') or request.args.get('merchant_order_id')
    
    if not order_id:
        print("Payment callback received but no order ID found")
        return render_template('payment_status.html', status='unknown', order_id=None)
    
    try:
        # Check payment status
        response = client.get_order_status(order_id, details=False)
        state = response.state
        
        # Log payment status to console
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*60}")
        print(f"[{timestamp}] PAYMENT CALLBACK RECEIVED")
        print(f"{'='*60}")
        print(f"Order ID: {order_id}")
        print(f"Status: {state}")
        print(f"{'='*60}\n")
        
        # Render status page
        return render_template('payment_status.html', 
                             status=state, 
                             order_id=order_id,
                             timestamp=timestamp)
    
    except Exception as e:
        print(f"Error in payment callback: {str(e)}")
        return render_template('payment_status.html', 
                             status='error', 
                             order_id=order_id,
                             error=str(e))

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True") == "True"
    app.run(debug=debug, host='0.0.0.0', port=port)


#test