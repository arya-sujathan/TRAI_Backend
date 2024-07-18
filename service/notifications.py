
from django.core.mail import send_mail
from django.conf import settings

def send_success_email(user_email, trade_type, symbol, order_id=None):
    print('success mail is sending ...........')
    subject = f"{trade_type} Trade Successful for {symbol}"
    message = f"Your {trade_type.lower()} trade for {symbol} was successful. "
    if trade_type.lower()!='close':
        message = message + f"Order ID: {order_id}"
    sender_email = settings.EMAIL_HOST_USER
    recipient_list = user_email

    send_mail(subject, message, sender_email, recipient_list)

def send_error_email(user_email, trade_type, symbol, error):
    subject = f"{trade_type} Trade Failed for {symbol}"
    message = f"Your {trade_type.lower()} trade for {symbol} failed. Error: {error}"
    sender_email = settings.EMAIL_HOST_USER
    recipient_list = user_email

    send_mail(subject, message, sender_email, recipient_list)
