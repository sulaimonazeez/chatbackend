from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserProfileView
from .views import FriendsList, MessageList

urlpatterns = [
  path("register/", views.register_user, name="register"),
  path("login/", views.login_user, name="login"),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),
    path('friends/', FriendsList.as_view(), name='friends-list'),
    path('messages/<int:user_id>/', MessageList.as_view(), name='message-list'),
    path("search/", views.SearchProfile.as_view(), name="make_search"),
    path("users/<int:id>/", views.ProfileView.as_view(), name="profiles"),
]

