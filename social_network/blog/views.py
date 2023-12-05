from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.db.models import Q
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import CustomUser, Post, Comment, FriendShipRelations, Like
from .forms import CustomUserCreationForm, CustomUserChangeForm, PostForm
from django.shortcuts import render, redirect, get_object_or_404
from .redis.redis_cache import get_posts_from_cache, set_posts_to_cache, get_random_posts_from_mongodb


def like_unlike_something(request, user_uuid, obj_uuid):
    referer = request.META.get('HTTP_REFERER')
    print(user_uuid, obj_uuid)
    like = Like.objects.filter(
            Q(who_likedId=user_uuid)&
            Q(liked_objId=obj_uuid)
            )
    if like:
        like.delete()
    else:
        like = Like(
                who_likedId=user_uuid,
                liked_objId=obj_uuid
                )
        like.save()
    return redirect(referer)

def write_comment(request, uuid):
    post = request.POST.get('commented_post')
    user = request.POST.get('commented_by')
    content = request.POST.get('content')
    comment = Comment(
            commented_post = post,
            commented_by = user,
            content = content
            )
    comment.save()
    return redirect('post-detail', uuid)


def send_friend_request(request, uuid):
    senderId = request.user.userId
    sender_username = request.user.username
    receiverId = CustomUser.objects.get(userId=uuid).userId
    receiver_username = CustomUser.objects.get(userId=uuid).username

    if not FriendShipRelations.objects.filter(senderId=senderId, receiverId=receiverId) or not FriendShipRelations.objects.filter(senderId=receiverId, receiverId=senderId):
        friend_request = FriendShipRelations(senderId=senderId, sender_username=sender_username, receiverId=receiverId, receiver_username=receiver_username, status='pending')
        friend_request.save()
        return redirect('user-detail', uuid)

    return redirect('user-detail', uuid)


def respond_to_friend_request(request, uuid):
    friend_request = get_object_or_404(FriendShipRelations, requestId=uuid)
    status = request.POST.get('action')
    print(status)
    if status:
        if status == 'accepted':
            friend_request.status = 'accepted'
        elif status == 'reject':
            friend_request.status = 'rejected'
    friend_request.save()

    return redirect('user-detail', request.user.userId)


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


class ChangeUserView(UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    success_url = reverse_lazy('login')
    template_name = 'change.html'

    def get_object(self, queryset=None, *args, **kwargs):
        uuid = self.kwargs.get('uuid')
        return self.model.objects.get(userId=uuid)


class CustomUserDetailView(DetailView):
    model = CustomUser
    template_name = 'user-detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['user'] = user
        posts = Post.objects.filter(authors=user.username).order_by('-views')[:10]
        context['posts'] = posts
        if self.request.user.is_authenticated:
            if self.request.user != user:
                has_relationship = FriendShipRelations.objects.filter(
                    Q(senderId=self.request.user.userId, receiverId=user.userId) |
                    Q(senderId=user.userId, receiverId=self.request.user.userId)
                    )
            else:
                has_relationship = FriendShipRelations.objects.filter(
                        Q(senderId=user.userId)|
                        Q(receiverId=user.userId)
                        )
                context['friends'] = FriendShipRelations.objects.filter(
                        (Q(senderId=user.userId)|
                        Q(receiverId=user.userId))&
                        Q(status='accepted')
                        )
                context['requests'] = FriendShipRelations.objects.filter(
                        Q(receiverId=user.userId)&
                        Q(status='pending')
                        )

        
            context['friend_request_exists'] = has_relationship

        return context

    def get_object(self, queryset=None, *args, **kwargs):
        uuid = self.kwargs.get('uuid')
        return self.model.objects.get(userId=uuid)


class UsersListView(ListView):
    model = CustomUser
    template_name = "user-list.html"

    def get_queryset(self):
        query = self.request.GET.get('q')

        if query:
            queryset = CustomUser.objects.filter(Q(username__icontains=query))
        else:
            queryset = CustomUser.objects.all()


        return queryset

class CreatePostView(LoginRequiredMixin, CreateView):
    form_class = PostForm
    success_url = reverse_lazy('home')
    template_name = 'posts/create.html'
    
    def form_valid(self, form):
        form.instance.authors = self.request.user.username
        return super().form_valid(form)


class ChangePostView(UpdateView):
    model = Post
    form_class = PostForm
    success_url = 'previous'
    template_name = 'posts/change.html'

    def get_success_url(self):
        if self.success_url == 'previous':
            return self.request.META.get('HTTP_REFERER', reverse_lazy('fallback-url-name'))
        return super().get_success_url()

    def get_object(self, queryset=None, *args, **kwargs):
        uuid = self.kwargs.get('uuid')
        return self.model.objects.get(postId=uuid)


class PostListView(ListView):
    model = Post
    template_name = 'posts/list.html'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q')
        order = self.request.GET.get('orderby', 'created_date')

        if query:
            queryset = Post.objects.filter(Q(title__icontains=query) | Q(content__icontains=query))
        else:
            queryset = Post.objects.all()

        queryset = queryset.order_by(order)

        return queryset


class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/detail.html'
    context_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = context['post']
        username = post.authors
        context["user"] = CustomUser.objects.get(username=username)
        comments = Comment.objects.filter(commented_post=post.postId)
        likes_count = Like.objects.filter(liked_objId=post.postId).count()
        context["likes"] = likes_count
        if comments:
            context["comments"] = comments
        
        return context

    def get_object(self, queryset=None, *args, **kwargs):
        uuid = self.kwargs.get('uuid')
        return self.model.objects.get(postId=uuid)


class TopPostsViews(ListView):
    model = Post
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Спробуємо отримати дані з кешу
        posts = get_posts_from_cache()
        if not posts:
            mongo_posts = get_random_posts_from_mongodb()
            set_posts_to_cache(mongo_posts)
            print(1)
            posts = get_posts_from_cache()



        context["posts"] = posts

        return context
'''def get_queryset(self):
        username = self.kwargs.get('username')
        order = self.request.GET.get('orderby', 'views')

        if username:
            user = CustomUser.objects.filter(username=username).first()
            if user:
                new_context = Post.objects.filter(author=username).order_by(order)
            else:
                new_context = Post.objects.none()
        else:
            new_context = Post.objects.order_by(order)

        return new_context

    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        context['filter'] = self.kwargs.get('username')
        context['orderby'] = self.request.GET.get('orderby', 'views')
        return context'''
