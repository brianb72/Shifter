import datetime
from shutil import rmtree

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from shifter_files.models import FileUpload

TEST_USER_EMAIL = "iama@test.com"
TEST_USER_PASSWORD = "mytemporarypassword"

TEST_USER_EMAIL_2 = "shifter@github.com"
TEST_USER_PASSWORD_2 = "mytemporarypassword"

TEST_FILE_NAME = "mytestfile.txt"
TEST_FILE_CONTENT = b"Hello, World!"


class FileDownloadViewTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(TEST_USER_EMAIL,
                                             TEST_USER_PASSWORD)

        self.user_2 = User.objects.create_user(TEST_USER_EMAIL_2,
                                               TEST_USER_PASSWORD_2)

    def tearDown(self):
        rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_download(self):
        client = Client()
        client.login(email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD)
        test_file = SimpleUploadedFile(TEST_FILE_NAME, TEST_FILE_CONTENT)
        file_upload = FileUpload.objects.create(
            owner=self.user, file_content=test_file,
            upload_datetime=timezone.now(),
            expiry_datetime=timezone.now() + datetime.timedelta(weeks=1),
            filename=TEST_FILE_NAME)
        url = reverse("shifter_files:file-download",
                      args=[file_upload.file_hex])
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['X-Accel-Redirect'],
                         file_upload.file_content.url)

    def test_download_anon_user(self):
        client = Client()
        client.login(email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD)
        test_file = SimpleUploadedFile(TEST_FILE_NAME, TEST_FILE_CONTENT)
        file_upload = FileUpload.objects.create(
            owner=self.user, file_content=test_file,
            upload_datetime=timezone.now(),
            expiry_datetime=timezone.now() + datetime.timedelta(weeks=1),
            filename=TEST_FILE_NAME)
        client_anon = Client()
        url = reverse("shifter_files:file-download",
                      args=[file_upload.file_hex])
        response = client_anon.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['X-Accel-Redirect'],
                         file_upload.file_content.url)

    def test_download_another_user(self):
        client = Client()
        client.login(email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD)
        client.login(email=TEST_USER_EMAIL_2, password=TEST_USER_PASSWORD_2)
        test_file = SimpleUploadedFile(TEST_FILE_NAME, TEST_FILE_CONTENT)
        file_upload = FileUpload.objects.create(
            owner=self.user, file_content=test_file,
            upload_datetime=timezone.now(),
            expiry_datetime=timezone.now() + datetime.timedelta(weeks=1),
            filename=TEST_FILE_NAME)
        client_2 = Client()
        url = reverse("shifter_files:file-download",
                      args=[file_upload.file_hex])
        response = client_2.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['X-Accel-Redirect'],
                         file_upload.file_content.url)

    def test_download_does_not_exist(self):
        client = Client()
        client.login(email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD)
        test_file = SimpleUploadedFile(TEST_FILE_NAME, TEST_FILE_CONTENT)
        FileUpload.objects.create(
            owner=self.user, file_content=test_file,
            upload_datetime=timezone.now(),
            expiry_datetime=timezone.now() + datetime.timedelta(weeks=1),
            filename=TEST_FILE_NAME)
        url = reverse("shifter_files:file-download",
                      args=['0'*32])
        response = client.get(url)
        self.assertEqual(response.status_code, 404)