from storages.backends.s3boto3 import S3Boto3Storage

class MediaStorage(S3Boto3Storage):
    location = 'qr_menu/'
    default_acl = 'public-read'
    file_overwrite = True
    querystring_auth = False

    def exists(self, name):
        # Override if your S3 provider doesn't support head_object
        # Return False to skip the check (since file_overwrite=True)
        return False