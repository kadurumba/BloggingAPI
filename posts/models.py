from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Blog(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=500)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blogs")
    likes_count = models.PositiveIntegerField(default=0)
    dislikes_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def likes_count(self):
        """Returns the number of likes for the blog."""
        return self.likes_dislikes.filter(is_like=True).count()

    @property
    def dislikes_count(self):
        """Returns the number of dislikes for the blog."""
        return self.likes_dislikes.filter(is_like=False).count()


class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, default='', null=True)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    content = models.TextField()
    likes_count = models.PositiveIntegerField(default=0)
    dislikes_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.blog.title}"

    @property
    def likes_count(self):
        """Returns the number of likes for the comment."""
        return self.likes_dislikes.filter(is_like=True).count()

    @property
    def dislikes_count(self):
        """Returns the number of dislikes for the comment."""
        return self.likes_dislikes.filter(is_like=False).count()


class LikeDislike(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="likes_dislikes",  null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes_dislikes", null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default='', null=True)
    is_like = models.BooleanField()
# True for like, False for dislike

    class Meta:
        unique_together = ('blog', 'user', 'comment')  # Prevent duplicate likes/dislikes

    def __str__(self):
        return f"{'Like' if self.is_like else 'Dislike'} by {self.user.username} on {'Blog' if self.blog else 'Comment'}"