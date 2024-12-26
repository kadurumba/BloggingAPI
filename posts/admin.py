from django.contrib import admin
from .models import Blog, Comment, LikeDislike

# Register your models here.


# Blog Admin Configuration
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'author__username')
    list_filter = ('created_at', 'updated_at', 'author')
    ordering = ('-created_at',)


# Comment Admin Configuration
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'blog', 'user', 'parent_comment', 'created_at')
    search_fields = ('text', 'blog__title', 'user__username')
    list_filter = ('created_at', 'blog', 'user')
    ordering = ('-created_at',)
    raw_id_fields = ('parent_comment',)  # Allows searching for parent comments by ID


# LikeDislike Admin Configuration
class LikeDislikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'blog', 'comment', 'user', 'is_like')
    search_fields = ('blog__title', 'comment__text', 'user__username')
    list_filter = ('is_like', 'blog', 'comment', 'user')
    ordering = ('blog', 'comment')


admin.site.register(Blog, BlogAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(LikeDislike, LikeDislikeAdmin)


