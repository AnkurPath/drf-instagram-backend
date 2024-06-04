from django.urls import path
from .views import UserSignupView, UserLoginView, UserNameUpdateAPIView, UserSearchAPIView, FriendRequestView, AcceptFriendRequestView, RejectFriendRequestView, ListFriendsView, ListPendingRequestsView

urlpatterns = [
    path('signup/',UserSignupView.as_view(),name = 'signup'),
    path('login/',UserLoginView.as_view(),name = 'login'),
    path('update_name/',UserNameUpdateAPIView.as_view(),name = 'update_name'),
    path('search/', UserSearchAPIView.as_view(), name='user_search'),
    path('friend-request/', FriendRequestView.as_view(), name='friend-request'),
    path('friend-request/accept/<int:pk>/', AcceptFriendRequestView.as_view(), name='accept-friend-request'),
    path('friend-request/reject/<int:pk>/', RejectFriendRequestView.as_view(), name='reject-friend-request'),
    path('friends/', ListFriendsView.as_view(), name='list-friends'),
    path('pending-requests/', ListPendingRequestsView.as_view(), name='list-pending-requests'),
]
