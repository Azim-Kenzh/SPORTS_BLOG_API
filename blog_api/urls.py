"""blog_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter

from account.views import UserViewSet
from main.views import *

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('posts', PostsViewSet)
router.register('comment', CommentViewSet)
router.register('likes', LikeViewSet)
router.register('favorites', FavoriteViewSet)
router.register('ratings', RatingViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title='Stack API',
        default_version='v1',
        description='Test description',
    ),
    public=True,
)


urlpatterns = [
    path('api/v1/docs/', schema_view.with_ui()),
    path('admin/', admin.site.urls),
    path('api/v1/accounts/', include('account.urls')),
    path('api/v1/news/', ParsAPIView.as_view()),
    path('api/v1/', include(router.urls)),
    path('api/v1/categories/', CategoryListView.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


