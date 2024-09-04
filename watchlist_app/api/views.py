from rest_framework.response import Response
# from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics
from rest_framework import viewsets
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle, ScopedRateThrottle

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from watchlist_app.api.permissions import IsAdminOrReadOnly, IsReviewUserOrReadOnly
from watchlist_app.models import WatchList, StreamPlatform, Review
from watchlist_app.api.serializers import WatchListSerializer, StreamPlatformSerializer, ReviewSerializer
from watchlist_app.api.throttling import ReviewCreateThrottle, ReviewListThrottle
from watchlist_app.api.pagination import WatchListPagination, WatchListLOPagination, WatchListCUPagination

class UserReview(generics.ListAPIView):
    serializer_class = ReviewSerializer
    # permission_classes = [IsReviewUserOrReadOnly]
    # throttle_classes = [ReviewListThrottle, AnonRateThrottle]

    # def get_queryset(self):
    #     username = self.kwargs['username']
    #     return Review.objects.filter(review_user__username=username)

    def get_queryset(self):
        username = self.request.query_params.get('username')
        return Review.objects.filter(review_user__username=username)


class ReviewList(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewUserOrReadOnly]
    throttle_classes = [ReviewListThrottle, AnonRateThrottle]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['review_user__username', 'activate']

    def get_queryset(self):
        watchlist_id = self.kwargs['pk']
        return Review.objects.filter(watchlist=watchlist_id)
    

class ReviewCreate(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ReviewCreateThrottle]

    def get_queryset(self):
        return Review.objects.all()
    

    def perform_create(self, serializer):
        watchlist_id = self.kwargs.get('pk')
        watchlist = WatchList.objects.get(pk=watchlist_id)

        review_user = self.request.user
        review_queryset = Review.objects.filter(watchlist=watchlist, review_user=review_user)

        if review_queryset.exists():
            raise ValidationError("You reviewed this movie already!")

        if watchlist.number_rating == 0:
            watchlist.avg_rating = serializer.validated_data['rating']
        else: 
            watchlist.avg_rating = (watchlist.avg_rating + serializer.validated_data['rating']) / 2

        watchlist.number_rating += 1
        watchlist.save()

        serializer.save(watchlist=watchlist, review_user=review_user)
    
    

class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewUserOrReadOnly]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'review-detail'

# class ReviewDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer

#     def get(self, request, *args, **kwargs):
#             return self.retrieve(request, *args, **kwargs)
    
#     def put(self, request, *args, **kwargs):
#             return self.update(request, *args, **kwargs)
    
#     def patch(self, request, *args, **kwargs):
#             return self.partial_update(request, *args, **kwargs)
    
#     def delete(self, request, *args, **kwargs):
#             return self.destroy(request, *args, **kwargs)

# class ReviewList(mixins.ListModelMixin,
#                   mixins.CreateModelMixin,
#                   generics.GenericAPIView):
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer

#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)


# class StreamPlatformViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = StreamPlatform.objects.all()
#     serializer_class = StreamPlatformSerializer
#     permission_classes = [IsAdminOrReadOnly]



class StreamPlatformViewSet(viewsets.ViewSet):

    queryset = StreamPlatform.objects.all()
    serializer_class = StreamPlatformSerializer
    permission_classes = [IsAdminOrReadOnly]

    def list(self, request):
        queryset = StreamPlatform.objects.all()
        serializer = StreamPlatformSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset =StreamPlatform.objects.all()
        watchlist = get_object_or_404(queryset, pk=pk)
        serializer = StreamPlatformSerializer(watchlist)
        return Response(serializer.data)
    
    def create(self, request):
        serializer = StreamPlatformSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StreamPlatformListAV(APIView):

    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        streamlist = StreamPlatform.objects.all()
        serializer = StreamPlatformSerializer(streamlist, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = StreamPlatformSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class StreamPlatformDetailAV(APIView):

    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, pk):
        try:
            stream = StreamPlatform.objects.get(pk=pk)
        except StreamPlatform.DoesNotExist:
            return Response({'Error':'Movie not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = StreamPlatformSerializer(stream)
        return Response(serializer.data)
    
    def put(self, request, pk):
        try:
            stream = StreamPlatform.objects.get(pk=pk)
        except StreamPlatform.DoesNotExist:
            return Response({'Error': 'StreamPlatform not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = StreamPlatformSerializer(stream, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            stream = StreamPlatform.objects.get(pk=pk)
        except StreamPlatform.DoesNotExist:
            return Response({'Error': 'StreamPlatform not found'}, status=status.HTTP_404_NOT_FOUND)
        
        stream.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WatchListGV(generics.ListAPIView):
    queryset = WatchList.objects.all()
    serializer_class = WatchListSerializer
    filter_backends = [filters.OrderingFilter]
    # ordering_fields  = ['avg_rating']
    pagination_class = WatchListCUPagination


class WatchListAV(APIView):

    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        movies = WatchList.objects.all()
        serializer = WatchListSerializer(movies, many=True)
        return Response(serializer.data)
    
    def post(self, request):

        serializer = WatchListSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class WatchListDetailAV(APIView):

    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, pk):
        try:
            movie_detail = WatchList.objects.get(pk=pk)
        except WatchList.DoesNotExist:
            return Response({'Error':'Movie not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = WatchListSerializer(movie_detail)
        return Response(serializer.data)
    
    def put(self, request, pk):
        movie_detail = WatchList.objects.get(pk=pk)
        serializer = WatchListSerializer(movie_detail, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_Request)

    def delete(self, request, pk):
        movie_detail = WatchList.objects.get(pk=pk)
        movie_detail.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




































# @api_view(['GET', 'POST'])
# def movie_list(request):
#     if request.method == 'GET':
#         movies = Movie.objects.all()
#         serializer = MovieSerializer(movies, many=True)
#         return Response(serializer.data)
    
#     if request.method == 'POST':
#         serializer = MovieSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_Request)

# @api_view(['GET', 'PUT', 'DELETE'])
# def movie_detail(request, pk):

#     if request.method == 'GET':
#         try:
#             movie_detail = Movie.objects.get(pk=pk)
#         except Movie.DoesNotExist:
#             return Response({'Error':'Movie not found'}, status=status.HTTP_404_NOT_FOUND)
#         serializer = MovieSerializer(movie_detail)
#         return Response(serializer.data)
    
#     if request.method == 'PUT':
#         movie_detail = Movie.objects.get(pk=pk)
#         serializer = MovieSerializer(movie_detail, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_Request)

#     if request.method == 'DELETE':
#         movie_detail = Movie.objects.get(pk=pk)
#         movie_detail.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


