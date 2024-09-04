from django.urls import path, include
from rest_framework.routers import DefaultRouter
from watchlist_app.api.views import *


router = DefaultRouter()
router.register('stream', StreamPlatformViewSet, basename='streamplatform')

urlpatterns = [
    path('list/', WatchListAV.as_view(), name='movie_list'),
    path('<int:pk>', WatchListDetailAV.as_view(), name='movie_detail'),

    path('', include(router.urls)),

    # path('stream/', StreamPlatformListAV.as_view(), name='stream'),
    # path('stream/<int:pk>', StreamPlatformDetailAV.as_view(), name='movie_detail'),

    path('<int:pk>/reviews/', ReviewList.as_view(), name='review-list'),
    path('<int:pk>/review-create/', ReviewCreate.as_view(), name='review-create'),
    path('review/<int:pk>/', ReviewDetail.as_view(), name='review-detail'),
    
    path('reviews/', UserReview.as_view(), name='user-review-detail1'),

    path('list2', WatchListGV.as_view(), name='watch-list')
]
