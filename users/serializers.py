from django.utils.timezone import now
from datetime import timedelta


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers

from django.contrib.auth import authenticate

from .models import User, Broker


class MyTokenObtainPairSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not username or not password:
            raise serializers.ValidationError('Username and password are required')

        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError('Invalid credentials')

        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': user.username,
            'email': user.email
        }


class UserCreatedByDefault(object):

    """
    This class is used to provide current signed in
    user value for  serializer
    """
    created_by = None

    def set_context(self, serializer_field):
        self.created_by = (
            serializer_field.context['request'].user)

    def __call__(self):
        return self.created_by

    def __repr__(self):
        return repr('%s()' % self.__class__.__name__)


class UserModifiedByDefault(object):

    """
    This class is used to provide current signed in
    user value for  serializer
    """
    modified_by = None

    def set_context(self, serializer_field):
        self.modified_by = (
            serializer_field.context['request'].user)

    def __call__(self):
        return self.modified_by

    def __repr__(self):
        return repr('%s()' % self.__class__.__name__)


class BrokerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Broker
        fields = ['id', 'name']
class CreateUserSerializer(serializers.ModelSerializer):
    broker = serializers.IntegerField(write_only=True)
    created_by = serializers.HiddenField(default=UserCreatedByDefault())
    modified_by = serializers.HiddenField(default=UserModifiedByDefault())

    class Meta:
        model = User
        fields = [
            'serialno', 'username', 'email', 'whatsapp_number', 
            'broker', 'server_id', 'date_of_registration',
            'date_of_expiry', 'lot_size', 'platform', 
            'created_on', 'modified_on', 'account_name',
            'password', 'created_by', 'modified_by',
            'is_active', 'is_staff', 'is_superuser'
        ]
        extra_kwargs = {
            'email': {'required': False},
            'whatsapp_number': {'required': False},
            'serialno': {'required': False},
        }

    def create(self, validated_data):
        broker_id = validated_data.pop('broker')
        
        try:
            broker = Broker.objects.get(id=broker_id)
        except Broker.DoesNotExist:
            raise serializers.ValidationError({'broker': 'Broker with this ID does not exist.'})
        
        validated_data['broker'] = broker
        
        # Generate the serial number
        last_user = User.objects.order_by('-id').first()
        if last_user and last_user.serialno.startswith('TRAI-'):
            last_serial_number = int(last_user.serialno.split('-')[1])
            new_serial_number = f'TRAI-{last_serial_number + 1:05d}'
        else:
            new_serial_number = 'TRAI-00001'
        
        validated_data['serialno'] = new_serial_number
        
        date_of_registration = validated_data.get('date_of_registration', now())
        validated_data['date_of_expiry'] = date_of_registration + timedelta(days=365)
        
        validated_data['is_active'] = True
        validated_data['is_staff'] = False
        validated_data['is_superuser'] = False
        validated_data['created_on'] = now()
        validated_data['modified_on'] = now()
        validated_data['plain_password'] = validated_data['password']
        
        user = User.objects.create(**validated_data)
        return user
    
class UserListSerializer(serializers.ModelSerializer):
    date_of_registration = serializers.SerializerMethodField()
    date_of_expiry = serializers.SerializerMethodField()
    broker = serializers.SerializerMethodField()
    whatsapp_number = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'serialno', 'username', 'date_of_registration', 'whatsapp_number',
            'email', 'broker', 'date_of_expiry', 'server_id'
        ]

    def get_date_of_registration(self, obj):
        if obj.date_of_registration:
            return obj.date_of_registration.strftime('%d-%m-%Y')
        return None

    def get_date_of_expiry(self, obj):
        if obj.date_of_expiry:
            return obj.date_of_expiry.strftime('%d-%m-%Y')
        return None
    
    def get_broker(self, obj):
        if obj.broker:
            return obj.broker.name or ''
        return None
    
    def get_whatsapp_number(self, obj):
        if obj.whatsapp_number:
            return obj.whatsapp_number
        return '---'
    
    def get_email(self, obj):
        if obj.email:
            return obj.email
        return '---'
