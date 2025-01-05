import hashlib
import hmac
import urllib.parse
from datetime import datetime


class VNPay:
    def __init__(self, tmn_code, hash_secret, url):
        self.tmn_code = tmn_code
        self.hash_secret = hash_secret
        self.url = url

    def create_payment_url(self, order_id, amount, return_url, ip_address):
        """Tạo URL thanh toán."""
        vnp_params = {
            "vnp_Version": "2.1.0",
            "vnp_Command": "pay",
            "vnp_TmnCode": self.tmn_code,
            "vnp_Amount": int(amount) * 100,
            "vnp_CurrCode": "VND",
            "vnp_TxnRef": order_id,
            "vnp_OrderInfo": f"Thanh toán đơn hàng {order_id}",
            "vnp_OrderType": "billpayment",
            "vnp_Locale": "vn",
            "vnp_ReturnUrl": return_url,
            "vnp_IpAddr": ip_address,
            "vnp_CreateDate": datetime.now().strftime("%Y%m%d%H%M%S"),
        }

        # Sắp xếp tham số
        sorted_params = sorted(vnp_params.items())
        query_string = "&".join(f"{key}={urllib.parse.quote_plus(str(value))}" for key, value in sorted_params)

        # Tạo hash
        hash_data = query_string.encode("utf-8")
        secure_hash = hmac.new(self.hash_secret.encode("utf-8"), hash_data, hashlib.sha512).hexdigest()

        # Thêm secure hash vào URL
        vnp_params["vnp_SecureHash"] = secure_hash
        query_string += f"&vnp_SecureHash={urllib.parse.quote_plus(secure_hash)}"

        return f"{self.url}?{query_string}"