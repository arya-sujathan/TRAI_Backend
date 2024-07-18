import json
import datetime

from datetime import timedelta
from collections import OrderedDict

from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Broker
from .serializers import MyTokenObtainPairSerializer, CreateUserSerializer, UserListSerializer, BrokerSerializer

class UserLoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # self.set_session_expiry(request)
        response_data = serializer.validated_data
        return Response(response_data, status=status.HTTP_200_OK)
    
class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    @staticmethod
    def get_logout_message():
        return ("You have been Logged out Successfully")

    @method_decorator(csrf_exempt)
    def post(self, request):
        try:
            
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            data = OrderedDict([
            ('state', 1), ('message', self.get_logout_message())
            ])
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    
class UserManagementView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_exempt)
    def post(self, request, format=None):
        serializer = CreateUserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @method_decorator(csrf_exempt)
    def get(self, request, format=None):
        users = User.objects.filter(is_staff=False, is_active=True)
        serializer = UserListSerializer(users, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class BrokerListView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_exempt)
    def get(self, request, format=None):
        brokers = Broker.objects.filter(is_active=True)
        serializer = BrokerSerializer(brokers, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
