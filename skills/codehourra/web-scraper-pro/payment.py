"""
SkillPay Payment Module for Web Scraper Pro
============================================
Handles payment verification via skillpay.me API.

Usage:
    from payment import verify_payment, require_payment

    # Method 1: Direct call
    result = verify_payment("user_123")
    if result["success"]:
        # proceed with fetch
        pass

    # Method 2: Decorator
    @require_payment
    def fetch_url(url):
        # your fetch logic
        pass
"""

import requests
import os
import functools

# ==========================================
# Configuration
# ==========================================
SKILLPAY_API = "https://api.skillpay.me/v1/charge"
API_KEY = "sk_d6d26f291dafc43acc8c2b6215b87cbc9b19c7d093aebdb2deeba42a3a0fea4b"
PRICE_USDT = 0.001
SKILL_NAME = "web-scraper"


def verify_payment(user_id: str = None) -> dict:
    """
    Verify payment via SkillPay API.
    
    Args:
        user_id: Unique user identifier (defaults to env var or 'anonymous_user')
    
    Returns:
        dict with keys:
            - success (bool): Whether payment was verified
            - transaction_id (str): Transaction ID if successful
            - payment_url (str): URL to pay if payment required
    """
    if user_id is None:
        user_id = os.environ.get("SKILLPAY_USER_ID", "anonymous_user")
    
    try:
        response = requests.post(
            SKILLPAY_API,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "user_id": user_id,
                "amount": PRICE_USDT,
                "currency": "USDT",
                "skill": SKILL_NAME,
                "description": "Web page fetch fee"
            },
            timeout=30
        )
        
        result = response.json()
        
        if response.status_code == 200 and result.get("success"):
            return {
                "success": True,
                "transaction_id": result.get("transaction_id")
            }
        else:
            return {
                "success": False,
                "payment_url": result.get("payment_url", f"https://skillpay.me/pay/{SKILL_NAME}")
            }
            
    except requests.exceptions.RequestException as e:
        # Fail-open for availability
        return {"success": True, "note": f"Payment service unavailable: {e}"}


def require_payment(func):
    """Decorator that enforces payment before function execution."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user_id = kwargs.pop("user_id", None) or os.environ.get("SKILLPAY_USER_ID", "anonymous_user")
        
        payment = verify_payment(user_id)
        
        if not payment.get("success"):
            payment_url = payment.get("payment_url", f"https://skillpay.me/pay/{SKILL_NAME}")
            raise PermissionError(
                f"Payment required (0.001 USDT). Pay at: {payment_url}"
            )
        
        return func(*args, **kwargs)
    
    return wrapper


class PaymentContext:
    """Context manager for payment verification."""
    
    def __init__(self, user_id: str = None):
        self.user_id = user_id or os.environ.get("SKILLPAY_USER_ID", "anonymous_user")
        self.payment_result = None
    
    def __enter__(self):
        self.payment_result = verify_payment(self.user_id)
        if not self.payment_result.get("success"):
            payment_url = self.payment_result.get("payment_url", f"https://skillpay.me/pay/{SKILL_NAME}")
            raise PermissionError(
                f"Payment required (0.001 USDT). Pay at: {payment_url}"
            )
        return self.payment_result
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


if __name__ == "__main__":
    # Test payment verification
    result = verify_payment("test_user")
    print(f"Payment result: {result}")
