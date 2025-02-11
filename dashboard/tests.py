from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

class DashboardViewTests(TestCase):

    def setUp(self):
        # Tạo user test
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_dashboard_index_not_logged_in(self):
        """
        Nếu chưa đăng nhập, truy cập / (dashboard_index) sẽ redirect tới login
        (vì có login_required)
        """
        url = reverse('dashboard_index')  # tên URL bạn đặt
        response = self.client.get(url)
        # Django mặc định redirect đến /accounts/login/?next=/ nếu login_required
        self.assertEqual(response.status_code, 302)  
        self.assertIn('/accounts/login/', response.url)

    def test_dashboard_index_logged_in(self):
        """
        Nếu đã đăng nhập, truy cập / (dashboard_index) sẽ thấy 200 OK
        """
        self.client.login(username='testuser', password='12345')
        url = reverse('dashboard_index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'user_count')
