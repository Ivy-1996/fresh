from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.conf import settings


class FdfsStorage(Storage):

    def __init__(self, client=None, img_domain=None):
        self.client = client if client else settings.FDFS_CLIENT_CONF
        self.img_domain = img_domain if img_domain else settings.IMG_URL

    def _save(self, name, content):
        client = Fdfs_client(self.client)
        response = client.upload_by_buffer(content.read())
        print(response)
        if response.get('Status') != 'Upload successed.':
            raise Exception('upload to fdfs failed')
        filename = response.get('Remote file_id')
        return filename

    def exists(self, name):
        return False

    def url(self, name):
        return self.img_domain + name
