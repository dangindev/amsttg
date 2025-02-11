# assets/tests/test_asset.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from assets.models.asset import Asset

class AssetModelTest(TestCase):
    def test_create_asset(self):
        asset = Asset.objects.create(name='Laptop', code='AS001', description='Dell XPS 13')
        self.assertEqual(str(asset), "Laptop (AS001)")
        self.assertTrue(Asset.objects.filter(code='AS001').exists())

class AssetViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.asset = Asset.objects.create(name='Phone', code='AS002', description='iPhone 14')

    def test_asset_list_not_logged_in(self):
        # Chưa login => asset_list -> redirect login (nếu login_required)
        url = reverse('asset_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_asset_list_logged_in(self):
        # Đăng nhập => 200 OK
        self.client.login(username='testuser', password='12345')
        url = reverse('asset_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Phone")

    def test_asset_detail_logged_in(self):
        self.client.login(username='testuser', password='12345')
        url = reverse('asset_detail', kwargs={'pk': self.asset.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "iPhone 14")
