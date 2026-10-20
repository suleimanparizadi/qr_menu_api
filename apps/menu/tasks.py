from celery import shared_task
from io import BytesIO
import qrcode
from django.conf import settings
from django.core.files.base import ContentFile
from apps.menu.models.menu_model import QRMenu
from utils.service_result import ServiceResult


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



