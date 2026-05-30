from flask import Blueprint, request, jsonify
import stripe
import paypalrestsdk
import os
from datetime import datetime

bp = Blueprint('payment', __name__, url_prefix='/api/payment')

# Initialize payment gateways
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
paypalrestsdk.configure({
    'mode': os.getenv('PAYPAL_MODE', 'sandbox'),
    'client_id': os.getenv('PAYPAL_CLIENT_ID'),
    'client_secret': os.getenv('PAYPAL_CLIENT_SECRET')
})

# Pricing plans
PLANS = {
    'free': {'price': 0, 'api_calls': 1000, 'name': 'Free Tier'},
    'pro': {'price': 999, 'api_calls': 50000, 'name': 'Pro Plan'},
    'business': {'price': 4999, 'api_calls': None, 'name': 'Business Plan'},
    'enterprise': {'price': 0, 'api_calls': None, 'name': 'Enterprise Plan'}
}

@bp.route('/plans', methods=['GET'])
def get_plans():
    """Get available pricing plans"""
    return jsonify({'plans': PLANS}), 200

@bp.route('/stripe/create-checkout', methods=['POST'])
def create_stripe_checkout():
    """Create Stripe checkout session"""
    data = request.get_json()
    plan = data.get('plan')
    
    if plan not in PLANS:
        return jsonify({'error': 'Invalid plan'}), 400
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': PLANS[plan]['name']},
                    'unit_amount': PLANS[plan]['price']
                },
                'quantity': 1
            }],
            mode='subscription',
            success_url='https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://yourdomain.com/cancel'
        )
        return jsonify({'checkout_url': checkout_session.url}), 200
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/paypal/create-payment', methods=['POST'])
def create_paypal_payment():
    """Create PayPal payment"""
    data = request.get_json()
    plan = data.get('plan')
    
    if plan not in PLANS:
        return jsonify({'error': 'Invalid plan'}), 400
    
    try:
        payment = paypalrestsdk.Payment({
            'intent': 'sale',
            'payer': {'payment_method': 'paypal'},
            'redirect_urls': {
                'return_url': 'https://yourdomain.com/paypal/return',
                'cancel_url': 'https://yourdomain.com/paypal/cancel'
            },
            'transactions': [{
                'amount': {
                    'total': str(PLANS[plan]['price'] / 100),
                    'currency': 'USD'
                },
                'description': PLANS[plan]['name']
            }]
        })
        
        if payment.create():
            return jsonify({'approval_url': payment.links[1]['href']}), 200
        else:
            return jsonify({'error': payment.error['message']}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET')
        )
        
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            # TODO: Update user plan in database
            pass
        
        return jsonify({'status': 'success'}), 200
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400

@bp.route('/webhook/paypal', methods=['POST'])
def paypal_webhook():
    """Handle PayPal webhook events"""
    data = request.get_json()
    
    if data['event_type'] == 'CHECKOUT.ORDER.COMPLETED':
        # TODO: Update user plan in database
        pass
    
    return jsonify({'status': 'success'}), 200
