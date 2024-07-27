from django.contrib.auth.models import Group, User
from django.contrib.auth import login, logout
from django.shortcuts import render
from rest_framework import permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from project.serializers import *
from project.permissions import IsSuperUser


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all the users
        for superusers and only the user himself/herself for non-superusers.
        """
        user = self.request.user
        if user.is_superuser:
            return User.objects.all().order_by('date_joined')
        return User.objects.filter(id=user.id).order_by('-date_joined')

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserEditSerializer

    def get_permissions(self):
        if self.request.user.is_superuser:
            return [IsSuperUser()]
        return [permissions.IsAuthenticated()]

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

'''
####  Create your views here. ####
'''

# Custom view for login
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        try:
            response = super(CustomAuthToken, self).post(request, *args, **kwargs)
            token = Token.objects.get(key=response.data['token'])
            return Response({
                'token': token.key,
                'user_id': token.user_id,
                'username': token.user.username
            })
        except Exception as e:
            return Response({"message": "Error logging in."}, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['GET'])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
# def example_view(request, format=None):
#     content = {
#         'user': str(request.user),  # `django.contrib.auth.User` instance.
#         'auth': str(request.auth),  # None
#     }
#     return Response(content)
    
# Custom view for logout
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        request.user.auth_token.delete()    
        logout(request)
        return Response({
            "message": "Successfully logged out."
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "Error logging out."}, status=status.HTTP_400_BAD_REQUEST)

# Custom view for registration
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_view(request):
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token = Token.objects.create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)