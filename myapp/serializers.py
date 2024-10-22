# serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Friends, Message


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )
        return user
        
        
        
    

class Profiles(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class FriendsSerializer(serializers.ModelSerializer):
    friend = UserSerializer(read_only=True)  # Nested serialization to show the friend's details
    
    class Meta:
        model = Friends
        fields = ['id', 'user', 'friend']


# Serializer for the Message model
class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['sender', 'receiver', 'message']
        #read_only_fields = ['timestamp', 'is_read']
