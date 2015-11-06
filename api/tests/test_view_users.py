from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

User = get_user_model()

class UsersViewTestCase(APITestCase):
    def setUp(self):
        self.password = 'johnpassword'
        self.user = User.objects.create_user('john', 'lennon@thebeatles.com', self.password, **{
            'first_name': 'John',
            'last_name': 'Lennon'
        })
        self.adminPassword = 'adminpassword'
        self.adminUser = User.objects.create_superuser('admin', 'admin@thebeatles.com', self.adminPassword, **{
            'first_name': 'The',
            'last_name': 'Administrator'
        })

    def login_user(self):
        url = reverse('obtain_jwt_token')
        data = {
            'username': self.user.username,
            'password': self.password
        }
        response = self.client.post(url, data, format='json')

        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.loggedIn = True
        self.adminLoggedIn = False

    def login_admin_user(self):
        url = reverse('obtain_jwt_token')
        data = {
            'username': self.adminUser.username,
            'password': self.adminPassword
        }
        response = self.client.post(url, data, format='json')

        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.loggedIn = True
        self.adminLoggedIn = True

    def test_anon_cannot_get_user_list(self):
        """
        Ensure we can't get a list of all users
        """
        url = reverse('v1:user-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anon_cannot_get_user_detail(self):
        """
        Ensure we can't get a user's details
        """
        url = reverse('v1:user-detail', args=(1,))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_get_user_list(self):
        """
        Ensure we can't get a list of all users
        """
        self.login_user()

        url = reverse('v1:user-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_get_user_list(self):
        """
        Ensure we can get a list of all users
        """
        self.login_admin_user()

        url = reverse('v1:user-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        user = response.data[0]
        self.assertEqual(user['username'], self.user.username)
        self.assertEqual(user['email'], self.user.email)
        self.assertEqual(user['first_name'], self.user.first_name)
        self.assertEqual(user['last_name'], self.user.last_name)

        user = response.data[1]
        self.assertEqual(user['username'], self.adminUser.username)
        self.assertEqual(user['email'], self.adminUser.email)
        self.assertEqual(user['first_name'], self.adminUser.first_name)
        self.assertEqual(user['last_name'], self.adminUser.last_name)

    def test_can_get_user_detail(self):
        """
        Ensure we can get our user details, and not others
        """
        self.login_user()

        url = reverse('v1:user-detail', args=('current',))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = response.data
        self.assertEqual(user['username'], self.user.username)
        self.assertEqual(user['email'], self.user.email)
        self.assertEqual(user['first_name'], self.user.first_name)
        self.assertEqual(user['last_name'], self.user.last_name)

        url = reverse('v1:user-detail', args=(self.user.id,))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = response.data
        self.assertEqual(user['username'], self.user.username)
        self.assertEqual(user['email'], self.user.email)
        self.assertEqual(user['first_name'], self.user.first_name)
        self.assertEqual(user['last_name'], self.user.last_name)

        url = reverse('v1:user-detail', args=(self.adminUser.id,))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_set_user_detail(self):
        """
        Ensure we can set our user details, and not others
        """
        self.login_user()

        url = reverse('v1:user-detail', args=('current',))
        data = {
            'first_name': 'Ringo',
            'last_name': 'Star',
            'email': 'star@thebeatles.com'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = response.data
        self.assertEqual(user['id'], self.user.id)
        self.assertEqual(user['username'], self.user.username)
        self.assertEqual(user['email'], 'star@thebeatles.com')
        self.assertEqual(user['first_name'], 'Ringo')
        self.assertEqual(user['last_name'], 'Star')

        data = {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email': self.user.email
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = response.data
        self.assertEqual(user['id'], self.user.id)
        self.assertEqual(user['username'], self.user.username)
        self.assertEqual(user['email'], self.user.email)
        self.assertEqual(user['first_name'], self.user.first_name)
        self.assertEqual(user['last_name'], self.user.last_name)

        data = {
            'username': 'rstar',
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = response.data
        self.assertEqual(user['id'], self.user.id)
        self.assertNotEqual(user['username'], 'rstar')
        self.assertEqual(user['username'], self.user.username)
        self.assertEqual(user['email'], self.user.email)
        self.assertEqual(user['first_name'], self.user.first_name)
        self.assertEqual(user['last_name'], self.user.last_name)

        url = reverse('v1:user-detail', args=(2,))
        data = {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email': self.user.email
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_set_user_password(self):
        """
        Ensure we can set our password
        """
        self.login_user()

        url = reverse('v1:user-detail', args=('current',))

        data = {
            'current_password': self.password,
            'new_password1': 'booyah',
            'new_password2': 'booyah',
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = response.data
        self.assertEqual(user['id'], self.user.id)
        self.assertEqual(user['username'], self.user.username)
        self.assertEqual(user['email'], self.user.email)
        self.assertEqual(user['first_name'], self.user.first_name)
        self.assertEqual(user['last_name'], self.user.last_name)

        data = {
            'current_password': 'booyah',
            'new_password1': self.password,
            'new_password2': self.password,
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = response.data
        self.assertEqual(user['id'], self.user.id)
        self.assertEqual(user['username'], self.user.username)
        self.assertEqual(user['email'], self.user.email)
        self.assertEqual(user['first_name'], self.user.first_name)
        self.assertEqual(user['last_name'], self.user.last_name)

        data = {
            'new_password1': 'booyah',
            'new_password2': 'booyah',
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['current_password'], ['You must enter your current password before you can change it.'])

        data = {
            'current_password': self.password,
            'new_password1': 'booya',
            'new_password2': 'booyah',
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['new_password1'], ['Your new password must be longer than 6 characters.'])

        data = {
            'current_password': self.password,
            'new_password1': self.password,
            'new_password2': self.password,
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['new_password1'], ['Your new password has to be different from your existing password.'])

        data = {
            'current_password': self.password,
            'new_password1': 'booyah',
            'new_password2': 'booyah1',
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['new_password2'], ['Your new password entries do not match.'])

        data = {
            'current_password': 'booyah',
            'new_password1': 'booyah1',
            'new_password2': 'booyah1',
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['current_password'], 'You entered the wrong password.')

        url = reverse('v1:user-detail', args=(2,))
        data = {
            'current_password': self.adminPassword,
            'new_password1': 'booyah',
            'new_password2': 'booyah',
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_get_user_detail(self):
        """
        Ensure we can get our user details, and others
        """
        self.login_admin_user()

        url = reverse('v1:user-detail', args=('current',))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = response.data
        self.assertEqual(user['username'], self.adminUser.username)
        self.assertEqual(user['email'], self.adminUser.email)
        self.assertEqual(user['first_name'], self.adminUser.first_name)
        self.assertEqual(user['last_name'], self.adminUser.last_name)

        url = reverse('v1:user-detail', args=(self.adminUser.id,))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = response.data
        self.assertEqual(user['username'], self.adminUser.username)
        self.assertEqual(user['email'], self.adminUser.email)
        self.assertEqual(user['first_name'], self.adminUser.first_name)
        self.assertEqual(user['last_name'], self.adminUser.last_name)

        url = reverse('v1:user-detail', args=(self.user.id,))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = response.data
        self.assertEqual(user['username'], self.user.username)
        self.assertEqual(user['email'], self.user.email)
        self.assertEqual(user['first_name'], self.user.first_name)
        self.assertEqual(user['last_name'], self.user.last_name)

    def test_admin_can_set_user_detail(self):
        """
        Ensure we can set our user details, and others
        """
        self.login_admin_user()

        url = reverse('v1:user-detail', args=('current',))
        data = {
            'first_name': 'Ringo',
            'last_name': 'Star',
            'email': 'star@thebeatles.com'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = response.data
        self.assertEqual(user['id'], self.adminUser.id)
        self.assertEqual(user['username'], self.adminUser.username)
        self.assertEqual(user['email'], 'star@thebeatles.com')
        self.assertEqual(user['first_name'], 'Ringo')
        self.assertEqual(user['last_name'], 'Star')

        data = {
            'first_name': self.adminUser.first_name,
            'last_name': self.adminUser.last_name,
            'email': self.adminUser.email
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = response.data
        self.assertEqual(user['id'], self.adminUser.id)
        self.assertEqual(user['username'], self.adminUser.username)
        self.assertEqual(user['email'], self.adminUser.email)
        self.assertEqual(user['first_name'], self.adminUser.first_name)
        self.assertEqual(user['last_name'], self.adminUser.last_name)

        url = reverse('v1:user-detail', args=(1,))
        data = {
            'first_name': self.adminUser.first_name,
            'last_name': self.adminUser.last_name,
            'email': self.adminUser.email
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = response.data
        self.assertEqual(user['id'], self.user.id)
        self.assertEqual(user['username'], self.user.username)
        self.assertEqual(user['email'], self.adminUser.email)
        self.assertEqual(user['first_name'], self.adminUser.first_name)
        self.assertEqual(user['last_name'], self.adminUser.last_name)

        url = reverse('v1:user-detail', args=(1,))
        data = {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email': self.user.email
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = response.data
        self.assertEqual(user['id'], self.user.id)
        self.assertEqual(user['username'], self.user.username)
        self.assertEqual(user['email'], self.user.email)
        self.assertEqual(user['first_name'], self.user.first_name)
        self.assertEqual(user['last_name'], self.user.last_name)

    def test_admin_can_set_user_password(self):
        """
        Ensure we can set our password and others
        """
        self.login_admin_user()

        url = reverse('v1:user-detail', args=('current',))

        data = {
            'current_password': self.adminPassword,
            'new_password1': 'booyah',
            'new_password2': 'booyah',
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = response.data
        self.assertEqual(user['id'], self.adminUser.id)
        self.assertEqual(user['username'], self.adminUser.username)
        self.assertEqual(user['email'], self.adminUser.email)
        self.assertEqual(user['first_name'], self.adminUser.first_name)
        self.assertEqual(user['last_name'], self.adminUser.last_name)

        data = {
            'current_password': 'booyah',
            'new_password1': self.adminPassword,
            'new_password2': self.adminPassword,
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = response.data
        self.assertEqual(user['id'], self.adminUser.id)
        self.assertEqual(user['username'], self.adminUser.username)
        self.assertEqual(user['email'], self.adminUser.email)
        self.assertEqual(user['first_name'], self.adminUser.first_name)
        self.assertEqual(user['last_name'], self.adminUser.last_name)

        url = reverse('v1:user-detail', args=(1,))

        data = {
            'current_password': self.password,
            'new_password1': 'booyah',
            'new_password2': 'booyah',
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = response.data
        self.assertEqual(user['id'], self.user.id)
        self.assertEqual(user['username'], self.user.username)
        self.assertEqual(user['email'], self.user.email)
        self.assertEqual(user['first_name'], self.user.first_name)
        self.assertEqual(user['last_name'], self.user.last_name)

        data = {
            'current_password': 'booyah',
            'new_password1': self.password,
            'new_password2': self.password,
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = response.data
        self.assertEqual(user['id'], self.user.id)
        self.assertEqual(user['username'], self.user.username)
        self.assertEqual(user['email'], self.user.email)
        self.assertEqual(user['first_name'], self.user.first_name)
        self.assertEqual(user['last_name'], self.user.last_name)

    def test_can_create_user(self):
        """
        Ensure we can create a new user
        """

        url = reverse('v1:user-list')
        data = {
            'username': 'rstar',
            'first_name': 'Ringo',
            'last_name': 'Star',
            'email': 'star@thebeatles.com',
            'new_password1': 'booyah',
            'new_password2': 'booyah'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = response.data
        self.assertTrue('id' in user)
        self.assertEqual(user['username'], 'rstar')
        self.assertEqual(user['email'], 'star@thebeatles.com')
        self.assertEqual(user['first_name'], 'Ringo')
        self.assertEqual(user['last_name'], 'Star')

    def test_new_user_cannot_login(self):
        """
        Ensure we cannot login with a newly created user
        """

        url = reverse('v1:user-list')
        data = {
            'username': 'rstar',
            'first_name': 'Ringo',
            'last_name': 'Star',
            'email': 'star@thebeatles.com',
            'new_password1': 'booyah',
            'new_password2': 'booyah'
        }
        response = self.client.post(url, data, format='json')

        url = reverse('obtain_jwt_token')
        data = {
            'username': 'rstar',
            'password': 'booyah'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('non_field_errors' in response.data)
