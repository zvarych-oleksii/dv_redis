from django.urls import path
from .views import SignUpView, ChangeUserView, CreatePostView, PostListView, PostDetailView, CustomUserDetailView, respond_to_friend_request, send_friend_request, write_comment, like_unlike_something, TopPostsViews, ChangePostView, UsersListView

urlpatterns = [
        path('signup/', SignUpView.as_view(), name='signup'),
        path('change/<uuid:uuid>', ChangeUserView.as_view(), name='user-change'),
        path('create-post/', CreatePostView.as_view(), name='create-post'),
        path('list-posts/', PostListView.as_view(), name='post-list'),
        path('detail-post/<uuid:uuid>', PostDetailView.as_view(), name='post-detail'),
        path('user/<uuid:uuid>', CustomUserDetailView.as_view(), name='user-detail'),
        path('send-friend-request/<uuid:uuid>', send_friend_request, name='send-friend-request'),
        path('respond-to-friend-request/<uuid:uuid>', respond_to_friend_request, name='respond-to-friend-request'),
        path('write-comment/<uuid:uuid>', write_comment, name='write-comment'),
        path('like-unlike-something/<uuid:user_uuid><uuid:obj_uuid>', like_unlike_something, name='like-unlike'),
        path('', TopPostsViews.as_view(), name="home"),
        path('update-post/<uuid:uuid>', ChangePostView.as_view(), name="change-post"),
        path('users/', UsersListView.as_view(), name="user-list")
        ]
