from django.urls import path
from .views import SellOperationView, BuyOperationView, CloseOperationView

urlpatterns = [
    path('sell/', SellOperationView.as_view(), name='sell-userstock'),
    path('buy/', BuyOperationView.as_view(), name='buy-userstock'),
    path('close/', CloseOperationView.as_view(), name='close-trade'),
]
