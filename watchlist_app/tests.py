from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from watchlist_app.api import serializers
from watchlist_app import models



# STREAMING PLATFORM TESTING
class StreamPlatformTestCase(APITestCase):

    # Seting up for testing

    def setUp(self):
        self.user = User.objects.create_user(username="example", password="Password@123")
        self.token = Token.objects.get(user__username=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.stream = models.StreamPlatform.objects.create(
            name="Hulu",
            about="#2 Streaming Platform",
            website='https://hulu.com'
        )
    # Creating a streaming platform
    def test_streamplatform_create(self):
        data = {
            'name': 'Netflix',
            'about' : "#1 Streaming Platform",
            'website' : 'https://netflix.com'
        }

        response = self.client.post(reverse('streamplatform-list'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Testing the list request
    def test_streamplatform_list(self):
        response = self.client.get(reverse('streamplatform-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Testing the detail 
    def test_streamplatform_ind(self):
        response = self.client.get(reverse('streamplatform-detail', args=(self.stream.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    
     # Testing the put request

    def test_streamplatform_put(self):
        data = {
            'name': 'Netflix',
            'about' : "#1 Streaming Platform",
            'website' : 'https://netflix1.com'
        }

        response = self.client.put(reverse('streamplatform-detail', args=(self.stream.id,)), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Testing the patch requet

    def test_streamplatform_patch(self):
        data = {
            'website' : 'https://netflix.com'
        }

        response = self.client.patch(reverse('streamplatform-detail', args=(self.stream.id,)), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Testing the delete request

    def test_streamplatform_delete(self):
        response = self.client.delete(reverse('streamplatform-detail', args=(self.stream.id,)))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

# WATCHLIST TESTING

class WatchListTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="example", password="Password@123")
        self.token = Token.objects.get(user__username=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.stream = models.StreamPlatform.objects.create(
            name="Hulu",
            about="#2 Streaming Platform",
            website='https://hulu.com'
        )

        self.watchlist = models.WatchList.objects.create(platform=self.stream, title="Example Movie", storyline="st", active=True)

    def test_watchlist_create(self):
        data = {
            "platform" : self.stream,
            "title" : "Example Movie",
            "storyline" : "Example Movie",
            "active" : True
        }
        response = self.client.post(reverse('movie_list'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_watchlist_list(self):
        response = self.client.get(reverse('movie_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_watchlist_ind(self):
        response = self.client.get(reverse('movie_detail', args=(self.watchlist.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.WatchList.objects.count(), 1)
        self.assertEqual(models.WatchList.objects.get().title, 'Example Movie')
        

    def test_watchlist_update(self):
        data = {
            "platform" : self.stream,
            "title" : "Eample Movie",
            "storyline" : "Eample Movie",
            "active" : False
        }

        response = self.client.put(reverse('movie_detail', args=(self.watchlist.id,)), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_watchlist_patch(self):
        data = {
            "title" : "Example Movie",
        }
        response = self.client.patch(reverse('movie_detail', args=(self.watchlist.id,)), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_watchlist_delete(self):
            response = self.client.delete(reverse('movie_detail', args=(self.watchlist.id,)))
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class ReviewTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="example", password="Password@123")
        self.token = Token.objects.get(user__username=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.stream = models.StreamPlatform.objects.create(
            name="Hulu",
            about="#2 Streaming Platform",
            website='https://hulu.com'
        )
        self.watchlist = models.WatchList.objects.create(platform=self.stream, title="Example Movie", storyline="st", active=True)
        self.watchlist2 = models.WatchList.objects.create(platform=self.stream, title="Example Movie2", storyline="st2", active=True)
        self.review = models.Review.objects.create( review_user=self.user,
                                                    rating=4,
                                                    description="Great Movie",
                                                    watchlist=self.watchlist2,
                                                    activate=True
                                                    )

    def test_review_create(self):
        data = {
            "review_user" : self.user,
            "rating" : 4,
            "description" : "Great Movie",
            "watchlist" : self.watchlist,
            "activate" : True
        }

        response = self.client.post(reverse('review-create', args = (self.watchlist.id,)), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Review.objects.count(), 2)

        response = self.client.post(reverse('review-create', args = (self.watchlist.id,)), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_review_create_unauth(self):
        data = {
            "review_user" : self.user,
            "rating" : 4,
            "description" : "Great Movie",
            "watchlist" : self.watchlist,
            "activate" : True
        }
        
        self.client.force_authenticate(user=None)
        response = self.client.post(reverse('review-create', args = (self.watchlist.id,)), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_review_update(self):
        data = {
            "review_user" : self.user,
            "rating" : 5,
            "description" : "Great Movie",
            "watchlist" : self.watchlist,
            "activate" : False
        }

        response = self.client.put(reverse('review-detail', args = (self.review.id, )), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_review_get_my_list(self):
        response = self.client.get(reverse('review-list', args=(self.watchlist.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_review_ind(self):
        response = self.client.get(reverse('review-detail', args=(self.review.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_review_delete(self):
        response = self.client.delete(reverse('review-detail', args=(self.review.id,)))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_review_user(self):
        response = self.client.get('/watch/reviews/?username' + self.user.username)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
