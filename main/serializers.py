from django.db.models import Avg
from rest_framework import serializers

from main.models import *


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d %B %Y - %H:%M', read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'category', 'title',  'text', 'created_at')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = instance.author.email
        representation['ratings'] = instance.ratings.all().aggregate(Avg('rating')).get('rating__avg')
        representation['likes'] = instance.likes.filter(like=True).count()
        representation['images'] = PostImageSerializer(instance.images.all(), many=True, context=self.context).data
        representation['comment'] = CommentSerializer(instance.comments.all(), many=True, context=self.context).data
        return representation



    def create(self, validated_data):
        request = self.context.get('request')
        user_id = request.user.id
        validated_data['author_id'] = user_id
        image_data = request.FILES
        post = Post.objects.create(**validated_data)
        for image in image_data.getlist('images'):
            PostImage.objects.create(image=image, post=post)
            print(image)
        return post


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = '__all__'

    def _get_image_url(self, obj):
        if obj.image:
            url = obj.image.url
            request = self.context.get('request')
            if request is not None:
                url = request.build_absolute_uri(url)
        else:
            url = ''
        return url

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['image'] = self._get_image_url(instance)
        return representation


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        exclude = ('author', )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = instance.author.email
        return representation

    def create(self, validated_data):
        request = self.context.get('request')
        user_id = request.user.id
        validated_data['author_id'] = user_id
        comment = Comment.objects.create(**validated_data)
        return comment


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ('id', 'post', 'author', 'like')

    def get_fields(self):
        action = self.context.get('action')
        fields = super().get_fields()
        if action == 'create':
            fields.pop('author')
            fields.pop('like')
        return fields

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        post = validated_data.get('post')
        like = Like.objects.get_or_create(author=user, post=post)[0]
        like.like = True if like.like is False else False
        like.save()
        return like


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('id', 'post', 'author', 'favorite')

    def get_fields(self):
        action = self.context.get('action')
        fields = super().get_fields()
        if action == 'create':
            fields.pop('author')
            fields.pop('favorite')
        return fields

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        post = validated_data.get('post')
        favorite = Favorite.objects.get_or_create(author=user, post=post)[0]
        favorite.favorite = True if favorite.favorite == False else False
        favorite.save()
        return favorite


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ('post', 'author', 'rating')

    def validate(self, attrs):
        rating = attrs.get('rating')
        if rating > 5:
            raise serializers.ValidationError('The value must not exceed 5')
        return attrs

    def get_fields(self):
        fields = super().get_fields()
        action = self.context.get('action')
        if action == 'create':
            fields.pop('author')
        return fields

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        post = validated_data.get('post')
        rat = validated_data.get('rating')
        rating = Rating.objects.get_or_create(author=user, post=post)[0]
        rating.rating = rat
        rating.save()
        return rating

class ParsSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=150)
    photo = serializers.CharField(max_length=255)