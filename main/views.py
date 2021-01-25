from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
from rest_framework.decorators import api_view, action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from .serializers import *
from .permissions import IsPostAuthor



# @api_view(['GET', 'POST'])
# def categories(request):
#     if request.method == 'GET':
#         categories = Category.objects.all()
#         serializer = CategorySerializer(categories, many=True)
#         return Response(serializer.data)
#     else:
#         return Response({"message": "Hello makers!"})
#
# class PostListView(APIView):
#     def get(self, request):
#         posts = Post.objects.all()
#         serializer = PostSerializer(posts, many=True)
#         return Response(serializer.data)
#
#     def post(self, request):
#         post = request.data
#         serializer = PostSerializer(data=post)
#         if serializer.is_valid(raise_exception=True):
#             post_saved = serializer.save()
#         return Response(serializer.data)


# ================

# class PostView(generics.ListCreateAPIView):
#     queryset = Post.objects.all()
#     serializer_class = PostSerializer
#
# class PostDetailedView(generics.RetrieveAPIView):
#     queryset = Post.objects.all()
#     serializer_class = PostSerializer
#
# class PostUpdateView(generics.UpdateAPIView):
#     queryset = Post.objects.all()
#     serializer_class = PostSerializer
#
# class PostDeleteView(generics.DestroyAPIView):
#     queryset = Post.objects.all()
#     serializer_class = PostSerializer

class MyPaginationClass(PageNumberPagination):
    page_size = 3

    def get_paginated_response(self, data):     #сокращаем текст поста, чтобы после троеточия заходить на сам пост
        # print(data[1])
        for i in range(self.page_size):
            text = data[i]['text']
            data[i]['text'] = text[:15] + '....'
            # print(data[1]['text'])
        return super().get_paginated_response(data)


class CategoryListView(generics. ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny, ]


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = MyPaginationClass

    def get_serializer_context(self):
        return {"request": self.request}

    def get_permissions(self):
        """ переопределим данный метод"""
        print(self.action)
        if self.action in ['update', 'partial_update', 'destroy']:
            permissions = [IsPostAuthor, ]
        else:
            permissions = [IsAuthenticated,]
        return[permission() for permission in permissions]

    def get_queryset(self):                     # фиьлтрация по неделям, когда созданы посты (можно сделать по дням)
        queryset = super().get_queryset()
        weeks_count = int(self.request.query_params.get('weeks', 0))
        print(self.request.query_params)
        if weeks_count > 0:
            start_date = timezone.now() - timedelta(weeks=weeks_count)
            queryset = queryset.filter(created_at__gte=start_date)  # gte -> greater than or equal
        return queryset

    @action(detail=False, methods=['get'])  #показ постов, созданных пользователем
    def own(self, request, pk=None):
        queryset = self.get_queryset()
        queryset = queryset.filter(author=request.user)
        serializer = PostSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])  #доступны только под ViewSet
    #router --> path posts/search
    def search(self, request, pk=None):
        # print(request.query_params)
        q = request.query_params.get('q')    # request.query_params  ==> request.GET
        queryset = self.get_queryset()
        queryset = queryset.filter(Q(title__icontains=q) |
                                   Q(text__icontains=q))
        serializer = PostSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class PostImageView(generics.ListCreateAPIView):
    queryset = PostImage.objects.all()
    serializer_class = PostImageSerializer

    def get_serializer_context(self):
        return {'request': self.request}


