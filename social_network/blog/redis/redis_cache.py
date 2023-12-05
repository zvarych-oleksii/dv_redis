import json
import redis
from ..models import Post
import random

def get_posts_from_cache():
    r = redis.StrictRedis(host='redis', port=6379, db=1, password='password')
    posts_key = 'random_posts'

    posts_data = r.get(posts_key)
    if posts_data:
        return json.loads(posts_data)
    else:
        return None

def set_posts_to_cache(posts):
    r = redis.StrictRedis(host='redis', port=6379, db=1, password='password')
    posts_key = 'random_posts'
    print(posts)

    r.set(posts_key, json.dumps(posts), ex=3)

def get_random_posts_from_mongodb():
    posts = list(Post.objects.all())
    random_posts = random.sample(posts, min(len(posts), 10))

    formatted_posts = [
        {
            "postId": str(post.postId),
            "title": post.title,
            "content": post.content,
            "created_date": post.created_date.isoformat(),
            "views": post.views,
            "authors": post.authors,
        }
        for post in random_posts
    ]
    print(formatted_posts)
    return formatted_posts

