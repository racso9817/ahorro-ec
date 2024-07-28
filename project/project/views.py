from django.contrib.auth.models import Group
from rest_framework import permissions, viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
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
            return CustomUser.objects.all().order_by('date_joined')
        return CustomUser.objects.filter(id=user.id).order_by('-date_joined')

    def get_serializer_class(self):
        if self.action == 'create':
            return RegisterSerializer
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
class MyTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        
        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.check_password(password):
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if the user already has a valid token
        refresh_token = None
        try:
            outstanding_token = OutstandingToken.objects.filter(user=user).first()
            if outstanding_token:
                blacklisted_token = BlacklistedToken.objects.filter(token=outstanding_token).first()
                if blacklisted_token:
                    raise TokenError("Token is blacklisted")
                else:
                    refresh_token = RefreshToken(outstanding_token.token)
                    access_token = refresh_token.access_token
                    return Response({
                        'refresh': str(refresh_token),
                        'access': str(access_token),
                    }, status=status.HTTP_200_OK)
        except TokenError:
            # If the token is blacklisted or invalid, create a new one
            refresh_token = RefreshToken.for_user(user)
        
        if refresh_token is None:
            refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token
        
        return Response({
            'refresh': str(refresh_token),
            'access': str(access_token),
        }, status=status.HTTP_200_OK)

# Example view
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def example_view(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)    
        content = {
            'id': str(request.user.id),
            'user': str(request.user),
            'email': str(request.user.email),
            'first_name': str(request.user.first_name),
            'last_name': str(request.user.last_name),
            'date_joined': str(request.user.date_joined),
            'is_authenticated': str(request.user.is_authenticated),
            'is_superuser': str(request.user.is_superuser),
            'is_staff': str(request.user.is_staff),
            'is_active': str(request.user.is_active)
        }
        return Response(content)
    except Exception as e:
        return Response({
            "message": "Error: " + str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    
# Custom view for logout
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        return Response({
            "message": "Successfully logged out."
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "message": "Error logging out: " + str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

# Custom view for register
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class UsersListView(generics.ListCreateAPIView):
    serializer_class = UserEditSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return CustomUser.objects.all().order_by('date_joined')
        return CustomUser.objects.filter(id=user.id).order_by('-date_joined')
    
    def get_permissions(self):
        if self.request.user.is_superuser:
            return [IsSuperUser()]
        return [permissions.IsAuthenticated()]
    
class UserEditView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserEditSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            if self.request.user.is_superuser:
                return [IsSuperUser()]
        return [permissions.IsAuthenticated()]

    def get_object(self):
        obj = super().get_object()
        if not self.request.user.is_superuser and obj.id != self.request.user.id:
            self.permission_denied(self.request, message="You do not have permission to perform this action.")
        return self.request.user