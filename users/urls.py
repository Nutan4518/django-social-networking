from django.urls import path
from .views import *

urlpatterns = [
    path("register-user/", RegisterUser.as_view(), name="signup"),
    path("login-user/", LoginUser.as_view()),
    path("search-user/", SearchUser.as_view()),
    path("send-friend-request/", SendRequest.as_view()),
    path("accept-friend-request/", AcceptRequest.as_view()),
    path("reject-friend-request/", RejectFriendRequest.as_view()),
    path("friends-list/", FriendsList.as_view()),
    path("pending-list/", PendingRequestsList.as_view()),
    path("rejected-list/", RejectedRequestsList.as_view()),
]
