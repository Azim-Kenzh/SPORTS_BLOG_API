from django.contrib.auth import authenticate
from rest_framework import serializers

from account.models import MyUser
from account.tasks import send_activation_code
from main.serializers import FavoriteSerializer


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, write_only=True)
    password_confirm = serializers.CharField(min_length=6, write_only=True)

    class Meta:
        model = MyUser
        fields = ('email', 'password', 'password_confirm')

    def validate(self, validate_data): # def validate - def clean, validate_data - clean_data
        password = validate_data.get('password')
        password_confirm = validate_data.get('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError('password do not match')
        return validate_data

    def create(self, validated_data):
        email = validated_data.get('email')
        password = validated_data.get('password')
        user = MyUser.objects.create_user(email=email, password=password)
        send_activation_code.delay(email=str(user.email), activation_code=str(user.activation_code))
        return user


#TODO: login serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        label='Password',
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, validate_data):
        email = validate_data.get('email')
        password = validate_data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                message = 'Пользователь не может залогин-ся'
                raise serializers.ValidationError(message, code='authorization')
        else:
            message = 'Must include "email" and "password"!'
            raise serializers.ValidationError(message, code='authorization')

        validate_data['user'] = user
        return validate_data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('email', )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        action = self.context.get('action')
        if action == 'retrieve':
            representation['favorites'] = FavoriteSerializer(instance.favorites.filter(favorite=True),
                                                             many=True, context=self.context).data
        return representation