from rest_framework import serializers
from .models import Blog, Comment, LikeDislike
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}, 'email': {'required': True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        user.save()
        return user


class BlogSerializer(serializers.ModelSerializer):

    class Meta:
        model = Blog
        fields = ['id', 'title', 'content', 'likes_count', 'dislikes_count', 'created_at', 'updated_at']

    def create(self, validated_data):
        user = self.context['request'].user         #Set the author to the logged-in user
        if not user.is_staff:                        #Ensure only admin users can create blogs
            raise serializers.ValidationError("You do not have permission to create a blog.")
        validated_data['author'] = user
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    parent_comment = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), required=False)
    replies = serializers.SerializerMethodField()  # A method to fetch the replies for each comment
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'blog', 'user', 'parent_comment', 'content', 'likes_count', 'dislikes_count', 'created_at', 'replies']

    def get_replies(self, obj):
        # Get replies to the current comment
        replies = Comment.objects.filter(parent_comment=obj)
        return CommentSerializer(replies, many=True).data

    def validate(self, data):
        if not data.get('blog') and not data.get('parent_comment'):
            raise serializers.ValidationError("Either blog or parent_comment must be provided.")

        if data.get('parent_comment') and not data.get('blog'):
            raise serializers.ValidationError("Cannot reply to a comment without specifying a blog.")

        return data

    def create(self, validated_data):
        user = validated_data.get('user', self.context['request'].user)
        return Comment.objects.create(user=user, **validated_data)


class LikeDislikeSerializer(serializers.ModelSerializer):
    action = serializers.ChoiceField(choices=['like', 'unlike', 'dislike', 'revert_dislike'], write_only=True)

    class Meta:
        model = LikeDislike
        fields = ['action']

    def validate(self, data):
        # Extract the user from the context (request)
        user = self.context['request'].user

        # Extract identifiers from the URL via the view context
        blog_id = self.context['view'].kwargs.get('blog_id')
        comment_id = self.context['view'].kwargs.get('comment_id')

        # Validate presence of target (either blog or comment)
        if not blog_id and not comment_id:
            raise serializers.ValidationError("A valid blog or comment ID must be provided.")

        if blog_id and comment_id:
            raise serializers.ValidationError("Cannot like/dislike both a blog and a comment in the same request.")

        # Retrieve the blog or comment
        blog = Blog.objects.filter(id=blog_id).first() if blog_id else None
        comment = Comment.objects.filter(id=comment_id).first() if comment_id else None

        if not blog and not comment:
            raise serializers.ValidationError("The specified blog or comment does not exist.")

        # Check for existing like/dislike by the user on the target
        existing_like_dislike = LikeDislike.objects.filter(user=user, blog=blog, comment=comment).first()
        action = data['action']

        # Validate actions
        if action == 'like':
            if existing_like_dislike:
                if existing_like_dislike.is_like:
                    raise serializers.ValidationError("You have already liked this.")
                existing_like_dislike.is_like = True
                existing_like_dislike.save()
                return data
            data['is_like'] = True

        elif action == 'unlike':
            if not existing_like_dislike or not existing_like_dislike.is_like:
                raise serializers.ValidationError("You cannot unlike something you haven't liked.")
            existing_like_dislike.delete()
            return data

        elif action == 'dislike':
            if existing_like_dislike:
                if not existing_like_dislike.is_like:
                    raise serializers.ValidationError("You have already disliked this.")
                existing_like_dislike.is_like = False
                existing_like_dislike.save()
                return data
            data['is_like'] = False

        elif action == 'revert_dislike':
            if not existing_like_dislike or existing_like_dislike.is_like:
                raise serializers.ValidationError("You cannot revert a dislike you haven't made.")
            existing_like_dislike.delete()
            return data

        # Assign validated target to data
        data['blog'] = blog
        data['comment'] = comment
        data['user'] = user
        return data

    def create(self, validated_data):
        """
        Create a new LikeDislike instance.
        """
        return LikeDislike.objects.create(
            blog=validated_data.get('blog'),
            comment=validated_data.get('comment'),
            user=validated_data.get('user'),
            is_like=validated_data.get('is_like')
        )