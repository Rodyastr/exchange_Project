# ads/tests.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Ad, ExchangeProposal
from rest_framework.test import APITestCase
from rest_framework import status

# Тесты модели
class AdModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser_model', password='testpassword')

    def test_ad_creation(self):
        ad = Ad.objects.create(
            user=self.user,
            title='Test Ad Model',
            description='This is a test description for model.',
            category='books',
            condition='new'
        )
        self.assertEqual(ad.title, 'Test Ad Model')
        self.assertEqual(ad.user, self.user)
        self.assertTrue(Ad.objects.filter(title='Test Ad Model').exists())

    def test_ad_str_representation(self):
        ad = Ad.objects.create(user=self.user, title='Another Ad Model', description='Desc', category='other', condition='used')
        self.assertEqual(str(ad), 'Another Ad Model')

# Тесты для представлений
class AdWebViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='webuser1_view', password='webpassword1')
        self.user2 = User.objects.create_user(username='webuser2_view', password='webpassword2')
        self.ad1 = Ad.objects.create(user=self.user1, title='Web Ad 1 View', description='Desc 1', category='books', condition='new')
        self.ad2 = Ad.objects.create(user=self.user2, title='Web Ad 2 View', description='Desc 2', category='electronics', condition='used')

    def test_ad_list_view(self):
        response = self.client.get(reverse('ad_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ads/ad_list.html')
        self.assertContains(response, 'Web Ad 1 View')
        self.assertContains(response, 'Web Ad 2 View')

    def test_ad_detail_view(self):
        response = self.client.get(reverse('ad_detail', args=[self.ad1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ads/ad_detail.html')
        self.assertContains(response, 'Web Ad 1 View')
        self.assertContains(response, 'Desc 1')

    def test_ad_create_view_authenticated(self):
        self.client.login(username='webuser1_view', password='webpassword1')
        response = self.client.post(reverse('ad_create'), {
            'title': 'New Web Ad Create', 'description': 'Description for new ad.', 'category': 'home', 'condition': 'good'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Ad.objects.filter(title='New Web Ad Create').exists())

    def test_ad_create_view_anonymous(self):
        response = self.client.get(reverse('ad_create'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('ad_create')}")


# Тесты для API
class AdAPITest(APITestCase):
    def setUp(self):
        Ad.objects.all().delete()
        User.objects.filter(username__in=['apiuser1_rest_adtest', 'apiuser2_rest_adtest']).delete()

        self.user1 = User.objects.create_user(username='apiuser1_rest_adtest', password='apipassword1')
        self.user2 = User.objects.create_user(username='apiuser2_rest_adtest', password='apipassword2')
        self.ad1 = Ad.objects.create(user=self.user1, title='API Ad 1 REST AdTest', description='Desc 1 REST', category='books', condition='new')
        self.ad2 = Ad.objects.create(user=self.user2, title='API Ad 2 REST AdTest', description='Desc 2 REST', category='electronics', condition='used')
        self.list_url = reverse('api_ad_list_create')
        self.detail_url_ad1 = reverse('api_ad_detail_update_delete', args=[self.ad1.pk])
        self.detail_url_ad2 = reverse('api_ad_detail_update_delete', args=[self.ad2.pk])

    def test_list_ads(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_ad(self):
        response = self.client.get(self.detail_url_ad1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.ad1.title)
        self.assertEqual(response.data['description'], self.ad1.description)


class ExchangeProposalAPITest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='ep_api_user1', password='ep_api_password1')
        self.user2 = User.objects.create_user(username='ep_api_user2', password='ep_api_password2')
        self.user3 = User.objects.create_user(username='ep_api_user3', password='ep_api_password3')

        self.ad1_user1 = Ad.objects.create(user=self.user1, title='EP_API Ad1 by U1', description='Desc1', category='books', condition='new')
        self.ad2_user1 = Ad.objects.create(user=self.user1, title='EP_API Ad2 by U1', description='Desc2', category='electronics', condition='used')
        self.ad3_user2 = Ad.objects.create(user=self.user2, title='EP_API Ad3 by U2', description='Desc3', category='home', condition='good')
        self.ad4_user2 = Ad.objects.create(user=self.user2, title='EP_API Ad4 by U2', description='Desc4', category='vehicles', condition='new')
        self.ad5_user3 = Ad.objects.create(user=self.user3, title='EP_API Ad5 by U3', description='Desc5', category='other', condition='new')


        self.proposal1 = ExchangeProposal.objects.create(
            ad_sender=self.ad1_user1,
            ad_receiver=self.ad3_user2,
            comment='EP_API P1 from U1 to U2'
        )

        self.proposal2 = ExchangeProposal.objects.create(
            ad_sender=self.ad4_user2,
            ad_receiver=self.ad2_user1,
            comment='EP_API P2 from U2 to U1'
        )
        self.list_create_url = reverse('api_exchange_proposal_list_create')


    def test_create_proposal_authenticated_success(self):
        self.client.force_authenticate(user=self.user1)

        data = {
            'ad_sender': self.ad2_user1.pk,
            'ad_receiver': self.ad4_user2.pk,
            'comment': 'New proposal from API, U1 to U2'
        }
        initial_proposal_count = ExchangeProposal.objects.count()
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExchangeProposal.objects.count(), initial_proposal_count + 1)
        self.assertEqual(response.data['ad_sender'], self.ad2_user1.pk)
        self.assertEqual(response.data['ad_receiver'], self.ad4_user2.pk)
        self.assertEqual(response.data['status'], 'pending')

    def test_create_proposal_authenticated_invalid_sender(self):
        self.client.force_authenticate(user=self.user1)

        data = {
            'ad_sender': self.ad3_user2.pk,
            'ad_receiver': self.ad1_user1.pk,
            'comment': 'Invalid proposal from API, U1 trying U2 ad'
        }
        initial_proposal_count = ExchangeProposal.objects.count()
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ExchangeProposal.objects.count(), initial_proposal_count)
        self.assertIn('ad_sender', response.data)

    def test_list_proposals_authenticated_participant(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        found_pks = {p['id'] for p in response.data['results']}
        self.assertIn(self.proposal1.pk, found_pks)
        self.assertIn(self.proposal2.pk, found_pks)

    def test_list_proposals_authenticated_non_participant(self):
        self.client.force_authenticate(user=self.user3)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)


    def test_list_proposals_unauthenticated(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def tearDown(self):
        ExchangeProposal.objects.all().delete()
        Ad.objects.filter(
            title__in=[
                'EP_API Ad1 by U1', 'EP_API Ad2 by U1',
                'EP_API Ad3 by U2', 'EP_API Ad4 by U2',
                'EP_API Ad5 by U3'
            ]
        ).delete()
        User.objects.filter(
            username__in=['ep_api_user1', 'ep_api_user2', 'ep_api_user3']
        ).delete()
