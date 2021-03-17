from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.utils import timezone
from rest_framework import generics, viewsets, status, reverse, mixins
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from main.models import *
from main.parsing import main
from main.permissions import IsPostAuthor
from main.serializers import *


MyUser = get_user_model()

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny, ]


class PostsViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, ]

    def get_serializer_context(self):
        return {'request': self.request}

    def get_permissions(self):
        if self.action == 'create':
            permissions = [IsAuthenticated, ]
        elif self.action in ['update', 'partial_update', 'delete']:
            permissions = [IsPostAuthor, ]
        else:
            permissions = []
        return [perm() for perm in permissions]

    """Фильтрация по неделям"""
    def get_queryset(self):
        queryset = super().get_queryset()
        days_count = int(self.request.query_params.get('days', 0))
        if days_count > 0:
            start_date = timezone.now() - timedelta(days=days_count)
            queryset = queryset.filter(created_at__gte=start_date)
        return queryset

    def get_queryset_rating(self):
        queryset = super().get_queryset()
        rating = int(self.request.query_params.get('rating', 0))
        if rating > 0:
            queryset = queryset.filter(ratings__gte=rating)
        return queryset

    @action(detail=False, methods=['get'])
    def own(self, request, pk=None):
        queryset = self.get_queryset()
        queryset = queryset.filter(author=request.user)
        serializer = PostSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    """Поиск"""
    @action(detail=False, methods=['get'])  # router build path post/search/?q=paris
    def search(self, request, pk=None):
        q = request.query_params.get('q')
        queryset = self.get_queryset()
        queryset = queryset.filter(Q(title__icontains=q) | Q(text__icontains=q))
        serializer = PostSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostImageView(generics.ListCreateAPIView):
    queryset = PostImage.objects.all()
    serializer_class = PostImageSerializer

    def get_serializer_context(self):
        return {'request': self.request}


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.action == 'create':
            permissions = [IsAuthenticated, ]
        elif self.action in ['update', 'partial_update', 'delete']:
            permissions = [IsPostAuthor, ]
        else:
            permissions = []
        return [perm() for perm in permissions]

    def get_serializer_context(self):
        return {'request': self.request, 'action': self.action}


class LikeViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated, ]

    def get_serializer_context(self):
        return {'request': self.request, 'action': self.action}


class FavoriteViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated, ]

    def get_serializer_context(self):
        return {'request': self.request, 'action': self.action}


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated, ]


    def get_serializer_context(self):
        return {'request': self.request, 'action': self.action}


class ParsAPIView(APIView):

    def get(self, request):
        dict_ = main()
        serializer = ParsSerializer(instance=dict_, many=True)
        return Response(serializer.data)