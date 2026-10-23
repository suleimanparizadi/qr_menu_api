from celery import shared_task
from io import BytesIO
import qrcode
import logging

from django.core.files.storage import default_storage
from django.conf import settings
from django.core.files.base import ContentFile
from apps.menu.models.menu_model import QRMenu


@shared_task
def generate_qr_code(menu_id):
        menu = QRMenu.objects.get(id=menu_id)
        qr_data = f"{settings.QR_MENU_BASE_URL}/menu/{menu.id}/"
        qr_image = qrcode.make(qr_data)
        qr_io = BytesIO()
        
        
        try:
            qr_image.save(qr_io, 'PNG')
            filename = f"menu-{menu.id}.png"

            menu.qr_code.save(
                  filename, ContentFile(qr_io.getvalue()), save=True
            )

        finally:
              qr_io.close()

        return {
        "success": True,
        "message": "QR code generated successfully",
        "menu_id": menu.id,
        }



logger = logging.getLogger(__name__)


@shared_task
def cleanup_orphaned_qr_codes():
    """
    Delete S3 QR files that don't belong to any menu.
    Runs every 3 days during low-traffic hours.
    """
    
    db_files = set(
        QRMenu.objects.exclude(qr_code='')
        .exclude(qr_code__isnull=True)
        .values_list('qr_code', flat=True)
    )

    # 2. List all files in the bucket (paginated)
    s3_files = set()
    try:
        paginator = default_storage.bucket.meta.client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=default_storage.bucket_name, Prefix=default_storage.location):
            for obj in page.get('Contents', []):
                s3_files.add(obj['Key'])
    except Exception as e:
        logger.error(f"S3 listing failed: {e}")
        return {"success": False, "error": str(e)}

    # 3. Find orphans (in S3 but not in DB)
    orphans = s3_files - db_files

    # 4. Delete them
    deleted = 0
    failed = 0
    for orphan in orphans:
        try:
            default_storage.delete(orphan)
            deleted += 1
        except Exception as e:
            logger.warning(f"Failed to delete {orphan}: {e}")
            failed += 1

    logger.info(f"QR cleanup: {deleted} deleted, {failed} failed, {len(orphans)} orphans found")

    return {
        "success": True,
        "orphans_found": len(orphans),
        "deleted": deleted,
        "failed": failed,
    }

