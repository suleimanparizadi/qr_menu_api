from django.db import models
from django.contrib.auth import get_user_model
import qrcode
from django.core.files import File
from io import BytesIO
from django.conf import settings


User = get_user_model()



class QRMenu(models.Model):

    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='menus')
    title = models.CharField(max_length=225)
    description = models.CharField(max_length=350, blank=True, null=True)
    qr_code = models.ImageField(upload_to='qr_menu/')
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def generate_qr_code(self):

        qr_data = f"{settings.QR_MENU_BASE_URL}/menu/{self.id}/"
        qr_image = qrcode.make(qr_data)
        qr_io = BytesIO()
        qr_image.save(qr_io, 'PNG')
        filename = f"menu-{self.id}.png"

        if self.qr_code and self.qr_code.storage.exists(self.qr_code.name):
            self.qr_code.delete(save=False)

        self.qr_code.save(filename, ContentFile=(qr_io.getvalue()), save=True)
        qr_io.close()


    def __str__(self):
        return f"{self.title} - {self.id}"



class MenuItem(models.Model):

    menu = models.ForeignKey(QRMenu, on_delete=models.CASCADE, related_name='items')
    item = models.CharField(max_length=225)
    description = models.CharField(max_length=225)
    price = models.IntegerField()
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.item} - {self.menu} - {self.id}"