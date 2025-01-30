from django.shortcuts import render

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .serializers import Profiles
from django.contrib.auth.models import User
from .serializers import FriendsSerializer, MessageSerializer
from .models import Friends, Message




@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Calls create() method in the serializer
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
        

@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user is not None:
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    else:
        return Response({'error': 'Invalid credentials'}, status=400)
        
        
        
        

class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            return Response({
                'access': response.data['access'],
                'refresh': response.data['refresh'],
                'message': 'Login successful!'
            })
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
            
            
            
          

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # Get the logged-in user
        serializer = Profiles(user)  # Serialize the user object
        return Response(serializer.data)
        
        

class SearchProfile(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get("query", None)
        
        if query:
            users = User.objects.filter(username__icontains=query)
            
            if users.exists():
                serializer = UserSerializer(users, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "No users found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"detail": "Query parameter 'q' is missing."}, status=status.HTTP_400_BAD_REQUEST)




class FriendsList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Retrieve friends for the logged-in user
        friends = Friends.objects.filter(user=request.user)

        if friends.exists():
            serializer = FriendsSerializer(friends, many=True)
            return Response(serializer.data)
        
        # Check if there is a default user (ID=1) and add them as a friend if no friends exist
        try:
            default_user = User.objects.get(id=1)
            if not Friends.objects.filter(user=request.user, friend=default_user).exists():
                Friends.objects.create(user=request.user, friend=default_user)
            friends = Friends.objects.filter(user=request.user)
            serializer = FriendsSerializer(friends, many=True)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"message": "No friends found and default user does not exist"}, status=404)

    def post(self, request):
        try:
            user_id = request.data.get("id")
            if not user_id:
                return Response({"message": "User ID is required"}, status=400)

            try:
                friend_user = User.objects.get(id=int(user_id))
            except User.DoesNotExist:
                return Response({"message": "User not found"}, status=404)

            # Check if friendship already exists
            if Friends.objects.filter(user=request.user, friend=friend_user).exists():
                return Response({"message": "Already in friend list"}, status=400)

            # Create a new friendship
            Friends.objects.create(user=request.user, friend=friend_user)
            return Response({"message": "Friend added successfully"}, status=201)

        except Exception as e:
            return Response({"message": f"Something went wrong: {str(e)}"}, status=500)


  



# View to handle messages between two users
class MessageList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            other_user = User.objects.get(id=int(user_id))
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        messages = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=other_user)) |
            (Q(sender=other_user) & Q(receiver=request.user))
        ).order_by('timestamp')

        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, user_id):
        try:
            other_user = User.objects.get(id=int(user_id))
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        message_content = request.data.get('message')

        if message_content:
            message = Message.objects.create(sender=request.user, receiver=other_user, message=message_content)
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'error': 'Message content cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)



class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            users = User.objects.get(id=id)
            return Response({"username":users.username, "status": "Online", "email":users.email, "firstname":users.first_name, "lastname": users.last_name
                             
                             })
        except User.DoesNotExist:
            return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)