# import_export/tests/test_import_export.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch
from import_export.tasks import import_data, export_data
import os

class ImportExportTest(TestCase):
    def setUp(self):
        # Tạo user, login
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        
        # Tạo 1 file CSV tạm
        self.test_csv_path = '/tmp/test_import.csv'
        with open(self.test_csv_path, 'w') as f:
            f.write("name,code\nLaptop,AS001\nPhone,AS002\n")

    def tearDown(self):
        # Xoá file sau test
        if os.path.exists(self.test_csv_path):
            os.remove(self.test_csv_path)

    @patch('import_export.tasks.import_data.delay')
    def test_import_file_view(self, mock_import_delay):
        """
        Kiểm tra khi POST file -> gọi import_data.delay
        """
        url = reverse('import_upload')
        with open(self.test_csv_path, 'rb') as f:
            response = self.client.post(url, {'file': f}, follow=True)

        self.assertEqual(response.status_code, 200)
        mock_import_delay.assert_called_once()

    def test_tasks_import_data_sync(self):
        """
        Gọi import_data(file_path) trực tiếp, xem kết quả
        """
        result = import_data(self.test_csv_path)
        self.assertEqual(result['status'], 'Import finished!')

    def test_tasks_export_data_sync(self):
        """
        Gọi export_data() trực tiếp, xem kết quả
        """
        result = export_data()
        self.assertEqual(result['status'], 'Export finished!')

    def test_import_progress_view_no_task(self):
        """
        Gọi /import-progress/<fake_id>/ -> PENDING
        """
        url = reverse('import_progress', kwargs={'task_id': 'fake_id_123'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'PENDING', response.content)
