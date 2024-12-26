"""
URL configuration for blogging project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from .views import BlogCreateView, BlogCommentView, LikeDislikeView, SignUpView, LoginView, LogoutView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


def home(request):
    return HttpResponse("Welcome to my API Home Page!")


urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('create_blog/', BlogCreateView.as_view(), name='create_blog'),
    path('blogs/<int:blog_id>/comments/', BlogCommentView.as_view(), name='comment_on_blog'),
    path('blogs/<int:blog_id>/', BlogCommentView.as_view(), name='all_blog_with_comments'),
    path('comments/<int:comment_id>/replies/', BlogCommentView.as_view(), name='comment_replies'),
    path('blogs/<int:blog_id>/like-dislike/', LikeDislikeView.as_view(), name='blog_like_dislike'),
    path('comments/<int:comment_id>/like-dislike/', LikeDislikeView.as_view(), name='comment_like_dislike'),
    path('api/blogs/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/blogs/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
