from storages.backends.s3boto3 import S3Boto3Storage

class MediaStorage(S3Boto3Storage):
    location = 'qr_menu/'
    default_acl = 'public-read'
    file_overwrite = True
    querystring_auth = False
