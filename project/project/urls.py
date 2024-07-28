"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from project import views
from project.views import *
from rest_framework_simplejwt import views as jwt_views

router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet, basename='user')
# router.register(r'groups', views.GroupViewSet, basename='group')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/login/', MyTokenObtainPairView.as_view(), name='api_login'),
    path('api/logout/', logout_view, name='api_logout'),
    path('api/register/', RegisterView.as_view(), name='api_register'),
    path('api/users/', UsersListView.as_view(), name='api_users'),
    path('api/users/<int:pk>/', UserEditView.as_view(), name='api_user_detail'),
    path('protected/', example_view, name='protected')
]
