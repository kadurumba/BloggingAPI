from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import filters, status, generics, permissions
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.contrib.auth import authenticate, login, logout
from posts.models import Blog, Comment, LikeDislike
from posts.serializers import UserSerializer, BlogSerializer, CommentSerializer, LikeDislikeSerializer
from django.db.models import Count


class SignUpView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer


# User Login View
class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer = UserSerializer

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        password = request.data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            access_token = AccessToken.for_user(user)

            user_data = UserSerializer(user).data

            return Response({
                'access': str(access_token), 'user': user_data
                             })
        else:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)


# User Logout View
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        logout(request)
        return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)


class BlogCreateView(APIView):
    """
    View to allow only admin users to create blog posts.
    """
    permission_classes = [IsAdminUser]  # Restrict access to admin users only

    def post(self, request, *args, **kwargs):
        serializer = BlogSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            blog = serializer.save()  # Save the blog post
            return Response(
                {"message": "Blog post created successfully", "blog": BlogSerializer(blog).data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class CommentView(APIView):
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#
#     def post(self, request, blog_id, *args, **kwargs):
#         """
#         Create a comment on a blog or reply to an existing comment.
#         """
#         data = request.data.copy()  # Create a mutable copy of the request data
#         data['blog'] = blog_id  # Inject blog_id into the data
#
#         serializer = CommentSerializer(data=data, context={'request': request})
#         if serializer.is_valid():
#             comment = serializer.save()
#             return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def get(self, request, blog_id, *args, **kwargs):
#         """
#         Retrieve comments for a specific blog.
#         """
#         try:
#             blog = Blog.objects.get(id=blog_id)
#         except Blog.DoesNotExist:
#             return Response({"error": "Blog not found."}, status=status.HTTP_404_NOT_FOUND)
#
#         # Fetch top-level comments (parent_comment=None) and include nested replies
#         comments = Comment.objects.filter(blog=blog, parent_comment=None).prefetch_related('replies')
#         serializer = CommentSerializer(comments, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)


class BlogCommentView(APIView):
    """
    Handles comments, nested replies, likes, and dislikes on blogs.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, blog_id=None, comment_id=None, *args, **kwargs):
        """
        Handles creating comments and replies on blogs.
        """
        data = request.data.copy()

        if blog_id:
            data['blog'] = blog_id  # Associate the comment with the blog
        elif comment_id:
            try:
                parent_comment = Comment.objects.get(id=comment_id)
                data['blog'] = parent_comment.blog_id  # Associate the reply with the blog of the parent comment
                data['parent_comment'] = comment_id  # Associate the reply with the parent comment
            except Comment.DoesNotExist:
                return Response({"error": "Parent comment not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            comment = serializer.save()  # Automatically assigns the user via the serializer's `create()` method
            return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, blog_id=None, *args, **kwargs):
        """
        Retrieve all comments for a blog and provide like/dislike counts and details.
        """
        try:
            blog = Blog.objects.get(id=blog_id)
        except Blog.DoesNotExist:
            return Response({"error": "Blog not found."}, status=status.HTTP_404_NOT_FOUND)

        # Fetch all top-level comments and their nested replies
        comments = Comment.objects.filter(blog=blog, parent_comment=None).prefetch_related('replies')
        blog_serializer = BlogSerializer(blog)
        comments_serializer = CommentSerializer(comments, many=True)
        return Response({
            "blog": blog_serializer.data,
            "comments": comments_serializer.data,
        },
            status=status.HTTP_200_OK)


class LikeDislikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = LikeDislikeSerializer(data=request.data, context={'request': request, 'view': self})
        if serializer.is_valid():
            action = serializer.validated_data.get('action')
            instance = serializer.save() if action in ['like', 'dislike'] else None
            return Response({
                "message": f"Successfully performed '{action}' action.",
                "data": LikeDislikeSerializer(instance).data if instance else None
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)