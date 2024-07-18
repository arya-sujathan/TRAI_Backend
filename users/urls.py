from django.urls import path
from .views import UserLoginView, UserManagementView, UserLogoutView, BrokerListView

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
    path('account/', UserManagementView.as_view(), name='user-account-management'),
    path('broker/', BrokerListView.as_view(), name='broker-list'),


]
