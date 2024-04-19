from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', RegistrationAPIView.as_view(), name='signup'),
    path("login/", LoginAPIView.as_view(), name="login"),
    path('search/', UserSearchAPIView.as_view(), name='user-search'),
    path('send-friend-request/<int:receiver_id>/', SendFriendRequestAPIView.as_view(), name='send-friend-request'),
    path('accept-friend-request/<int:request_id>/', AcceptFriendRequestAPIView.as_view(), name='accept-friend-request'),
    path('reject-friend-request/<int:request_id>/', RejectFriendRequestAPIView.as_view(), name='reject-friend-request'),
    path('list-friends/', ListFriendsAPIView.as_view(), name='list-friends'),
    path('list-pending-friend-requests/', ListPendingFriendRequestsAPIView.as_view(), name='list-pending-friend-requests'),
]
