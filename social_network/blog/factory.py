import factory
import random
from .models import Post, CustomUser, Comment, Like
from factory.faker import faker
from django.contrib.auth.hashers import make_password


fake = faker.Faker()



class CustomUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

    @factory.lazy_attribute
    def password(self):
        return make_password('1Password.')

class PostFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Post
    title = factory.Faker("sentence", nb_words=4)
    content = fake.paragraph(nb_sentences=20)
    views = factory.Faker('random_int', min=1, max=100)

    @factory.lazy_attribute
    def authors(self):
        usernames = [user['username'] for user in CustomUser.objects.values('username')]
        username = random.choice(usernames)
        return username

class CommentFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Comment

    content = fake.paragraph(nb_sentences=2)

    @factory.lazy_attribute
    def commented_post(self):
        posts = [post['postId'] for post in Post.objects.values("postId")]
        postId = random.choice(posts)
        return postId

    @factory.lazy_attribute
    def commented_by(self):
        usernames = [user['username'] for user in CustomUser.objects.values('username')]
        username = random.choice(usernames)
        return username
    

class LikeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Like
   
    @factory.lazy_attribute
    def liked_objId(self):
        posts = [post['postId'] for post in Post.objects.values("postId")]
        postId = random.choice(posts)
        return postId

    @factory.lazy_attribute
    def who_likedId(self):
        userIds = [user['userId'] for user in CustomUser.objects.values('userId')]
        userId = random.choice(userIds)
        return userId


def create_test_db():
    CustomUserFactory.create_batch(20)
    PostFactory.create_batch(100)
    CommentFactory.create_batch(200)
    LikeFactory.create_batch(1000)
