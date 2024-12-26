from django.core.files.storage import Storage
from django.conf import settings


class FastDFSStorage(Storage):
    """Customized File Storage Classes"""
    def __init__(self, fdfs_base_url=None):
        # if not fdfs_base_url:
        #     self.fdfs_base_url = settings.FDFS_BASE_URL
        # self.fdfs_base_url = fdfs_base_url
        self.fdfs_base_url = fdfs_base_url or settings.FDFS_BASE_URL

    def _open(self, name, mode='rb'):
        """which is called when opening a file and must be overridden."""
        # Since we are not currently opening a file, this method is currently useless, but it must be rewritten, so pass
        pass

    def _save(self, name, content):
        """which will be called when the file is saved"""
        # Because it's not currently going to save the file.
        pass

    def url(self, name):
        """Returns the full path of the file"""
        return self.fdfs_base_url + name

