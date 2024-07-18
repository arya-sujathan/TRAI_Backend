
from .models import TransactionHistory
from users.models import  User



def create_transaction_history(kwargs):

    user = kwargs.get('user')
    transaction_type = kwargs.get('transaction_type')
    stop_loss = kwargs.get('stop_loss')
    target = kwargs.get('target')
    open_price = kwargs.get('open_price')
    request_user_id = kwargs.get('request_user_id')


    # Create and save TransactionHistory object
    transaction = TransactionHistory(
        user_id=user,
        transaction_type=transaction_type,
        stop_loss=stop_loss,
        target=target,
        open_price=open_price,
        created_by_id=request_user_id,
        modified_by_id=request_user_id
    )
    transaction.save()
    return transaction