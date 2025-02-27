from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

# Function to generate JWT tokens
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# Signup API
@api_view(['POST'])
def signup(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password)
    return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)

# Login API
@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user is not None:
        tokens = get_tokens_for_user(user)
        return Response({
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'username': user.username  # Return username in response
        }, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

# Authentication Status API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def auth_status(request):
    user = request.user
    return Response({
        "isAuthenticated": True,
        "user": {
            "id": user.id,
            "username": user.username,
        }
    }, status=status.HTTP_200_OK)

# Logout API
@api_view(['POST'])
def logout(request):
    return Response({"message": "User logged out successfully"}, status=status.HTTP_200_OK)
