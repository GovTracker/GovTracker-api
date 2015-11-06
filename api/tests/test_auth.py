from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

User = get_user_model()

class JWTAuthTestCase(APITestCase):
    def setUp(self):
        self.password = 'johnpassword'
        self.user = User.objects.create_user('john', 'lennon@thebeatles.com', self.password, **{
            'first_name': 'John',
            'last_name': 'Lennon'
        })

    def test_can_obtain_jwt(self):
        """
        Ensure we can obtain a JWT
        """

        url = reverse('obtain_jwt_token')
        data = {
            'username': self.user.username,
            'password': self.password
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)

    def test_can_verify_jwt(self):
        """
        Ensure we can verify a JWT
        """

        url = reverse('obtain_jwt_token')
        data = {
            'username': self.user.username,
            'password': self.password
        }
        response = self.client.post(url, data, format='json')

        token = response.data['token']
        url = reverse('verify_jwt_token')
        data = {
            'token': token
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['token'], token)

    def test_can_refresh_jwt(self):
        """
        Ensure we can refresh a JWT
        """

        url = reverse('obtain_jwt_token')
        data = {
            'username': self.user.username,
            'password': self.password
        }
        response = self.client.post(url, data, format='json')
        import time
        time.sleep(1) # delay so we get a different token

        token = response.data['token']
        url = reverse('refresh_jwt_token')
        data = {
            'token': token
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['token'], token)

    def test_can_access_API_with_jwt(self):
        """
        Ensure we can authenticate with a JWT
        """

        url = reverse('obtain_jwt_token')
        data = {
            'username': self.user.username,
            'password': self.password
        }
        response = self.client.post(url, data, format='json')

        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        url = reverse('v1:user-detail', args=('current',))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
